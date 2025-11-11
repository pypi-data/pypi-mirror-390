// 单色并行FDTD
// 不考虑金属
// 第一个是光源并行维度,针对不同的偏振,入射角并行.
// 第二个是结构并行维度,针对不同的结构并行,用于鲁棒性/结构扫描
// 最后一个维度是频率并行维度,一般只有bloch边界需要
// 后续的测试,包括bloch,子像素平滑精度测试,多体并行
// 这里面就不放和FDTD一样的函数了
#include <torch/extension.h>
#include <torch/torch.h>
#include <vector>
#include <complex>
#include <thrust/complex.h>
// 常量定义
#define PI 3.14159265358979323846f
#define EPSILONf 1e-4f
// 常数内存变量定义,似乎必须先定义大小?然后在任何函数中都可以任意使用.CUDA中可以通过cudaMemcpyToSymbol修改常量

// 一维化的好处是不会浪费显存,且会快一些.但是多维数组仍然保留
// PML的起点为完整Yee网格的起点,终点为一半
// 暂时不管的函数:J注入和周期性
// x,y,z的最大网格数为 65,535
__global__ void Update_H_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hx,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hy,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hz,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ez,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cx2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cy2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz2,
    torch::PackedTensorAccessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t> PsixH,
    torch::PackedTensorAccessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t> PsiyH,
    torch::PackedTensorAccessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t> PsizH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bxH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> byH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bzH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cxH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cyH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> czH,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> PML_num,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny, const int nz)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies;                    // 对频率数量取模得到频率索引

    if (x >= nx || y >= ny || z >= nz)
        return;

    Hy[source_index][structure_index][x][y][z][frequency_index] +=
        Cx2[x] * (Ez[source_index][structure_index][x + 1][y][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);
    Hz[source_index][structure_index][x][y][z][frequency_index] -=
        Cx2[x] * (Ey[source_index][structure_index][x + 1][y][z][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);

    Hz[source_index][structure_index][x][y][z][frequency_index] +=
        Cy2[y] * (Ex[source_index][structure_index][x][y + 1][z][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);
    Hx[source_index][structure_index][x][y][z][frequency_index] -=
        Cy2[y] * (Ez[source_index][structure_index][x][y + 1][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);

    Hx[source_index][structure_index][x][y][z][frequency_index] +=
        Cz2[z] * (Ey[source_index][structure_index][x][y][z + 1][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);
    Hy[source_index][structure_index][x][y][z][frequency_index] -=
        Cz2[z] * (Ex[source_index][structure_index][x][y][z + 1][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);

    // 最后一格根本不需要Psi
    // 都是以Yee网格的最左侧为起点.
    //  xPML updates for the beginning and end of the grid
    if (x < PML_num[0])
    {
        PsixH[source_index][structure_index][x][y][z][0][frequency_index] =
            bxH[x] * PsixH[source_index][structure_index][x][y][z][0][frequency_index] +
            cxH[x] * (Ez[source_index][structure_index][x + 1][y][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);
        Hy[source_index][structure_index][x][y][z][frequency_index] +=
            PsixH[source_index][structure_index][x][y][z][0][frequency_index];
        PsixH[source_index][structure_index][x][y][z][1][frequency_index] =
            bxH[x] * PsixH[source_index][structure_index][x][y][z][1][frequency_index] -
            cxH[x] * (Ey[source_index][structure_index][x + 1][y][z][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);
        Hz[source_index][structure_index][x][y][z][frequency_index] +=
            PsixH[source_index][structure_index][x][y][z][1][frequency_index];
    }
    else if (x >= (nx - PML_num[0]))
    {
        uint16_t x0 = x - nx + 2 * PML_num[0];
        PsixH[source_index][structure_index][x0][y][z][0][frequency_index] =
            bxH[x0] * PsixH[source_index][structure_index][x0][y][z][0][frequency_index] +
            cxH[x0] * (Ez[source_index][structure_index][x + 1][y][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);
        Hy[source_index][structure_index][x][y][z][frequency_index] +=
            PsixH[source_index][structure_index][x0][y][z][0][frequency_index];
        PsixH[source_index][structure_index][x0][y][z][1][frequency_index] =
            bxH[x0] * PsixH[source_index][structure_index][x0][y][z][1][frequency_index] -
            cxH[x0] * (Ey[source_index][structure_index][x + 1][y][z][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);
        Hz[source_index][structure_index][x][y][z][frequency_index] +=
            PsixH[source_index][structure_index][x0][y][z][1][frequency_index];
    }

    // yPML updates for the beginning and end of the grid
    if (y < PML_num[1])
    {
        PsiyH[source_index][structure_index][x][y][z][0][frequency_index] =
            byH[y] * PsiyH[source_index][structure_index][x][y][z][0][frequency_index] +
            cyH[y] * (Ex[source_index][structure_index][x][y + 1][z][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);
        Hz[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyH[source_index][structure_index][x][y][z][0][frequency_index];
        PsiyH[source_index][structure_index][x][y][z][1][frequency_index] =
            byH[y] * PsiyH[source_index][structure_index][x][y][z][1][frequency_index] -
            cyH[y] * (Ez[source_index][structure_index][x][y + 1][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);
        Hx[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyH[source_index][structure_index][x][y][z][1][frequency_index];
    }
    else if (y >= (ny - PML_num[1]))
    {
        uint16_t y0 = y - ny + 2 * PML_num[1];
        PsiyH[source_index][structure_index][x][y0][z][0][frequency_index] =
            byH[y0] * PsiyH[source_index][structure_index][x][y0][z][0][frequency_index] +
            cyH[y0] * (Ex[source_index][structure_index][x][y + 1][z][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);
        Hz[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyH[source_index][structure_index][x][y0][z][0][frequency_index];
        PsiyH[source_index][structure_index][x][y0][z][1][frequency_index] =
            byH[y0] * PsiyH[source_index][structure_index][x][y0][z][1][frequency_index] -
            cyH[y0] * (Ez[source_index][structure_index][x][y + 1][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);
        Hx[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyH[source_index][structure_index][x][y0][z][1][frequency_index];
    }

    // zPML updates for the beginning and end of the grid
    if (z < PML_num[2])
    {
        PsizH[source_index][structure_index][x][y][z][0][frequency_index] =
            bzH[z] * PsizH[source_index][structure_index][x][y][z][0][frequency_index] +
            czH[z] * (Ey[source_index][structure_index][x][y][z + 1][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);
        Hx[source_index][structure_index][x][y][z][frequency_index] +=
            PsizH[source_index][structure_index][x][y][z][0][frequency_index];
        PsizH[source_index][structure_index][x][y][z][1][frequency_index] =
            bzH[z] * PsizH[source_index][structure_index][x][y][z][1][frequency_index] -
            czH[z] * (Ex[source_index][structure_index][x][y][z + 1][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);
        Hy[source_index][structure_index][x][y][z][frequency_index] +=
            PsizH[source_index][structure_index][x][y][z][1][frequency_index];
    }
    else if (z >= (nz - PML_num[2]))
    {
        uint16_t z0 = z - nz + 2 * PML_num[2];
        PsizH[source_index][structure_index][x][y][z0][0][frequency_index] =
            bzH[z0] * PsizH[source_index][structure_index][x][y][z0][0][frequency_index] +
            czH[z0] * (Ey[source_index][structure_index][x][y][z + 1][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);
        Hx[source_index][structure_index][x][y][z][frequency_index] +=
            PsizH[source_index][structure_index][x][y][z0][0][frequency_index];
        PsizH[source_index][structure_index][x][y][z0][1][frequency_index] =
            bzH[z0] * PsizH[source_index][structure_index][x][y][z0][1][frequency_index] -
            czH[z0] * (Ex[source_index][structure_index][x][y][z + 1][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);
        Hy[source_index][structure_index][x][y][z][frequency_index] +=
            PsizH[source_index][structure_index][x][y][z0][1][frequency_index];
    }
}

void Update_H(torch::Tensor &Hx, torch::Tensor &Hy, torch::Tensor &Hz, torch::Tensor &Ex, torch::Tensor &Ey, torch::Tensor &Ez, torch::Tensor &Cx2, torch::Tensor &Cy2, torch::Tensor &Cz2, torch::Tensor &PsixH, torch::Tensor &PsiyH, torch::Tensor &PsizH, torch::Tensor &bxH, torch::Tensor &byH, torch::Tensor &bzH, torch::Tensor &cxH, torch::Tensor &cyH, torch::Tensor &czH, torch::Tensor &PML_num, torch::Tensor &Periodic_num)
{
    // 分配线程和块
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int nx = Ex.size(2);
    const int ny = Ey.size(3);
    const int nz = Ez.size(4);
    const int num_frequencies = Ex.size(5);

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    Update_H_GPU<<<blocks, threads>>>(
        Hx.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Hy.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Hz.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ex.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Cx2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cy2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cz2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PsixH.packed_accessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t>(),
        PsiyH.packed_accessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t>(),
        PsizH.packed_accessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t>(),
        bxH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        byH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        bzH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cxH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cyH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        czH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PML_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz);
}

__global__ void Update_E_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hx,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hy,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hz,
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> epsbeta_x,
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> epsbeta_y,
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> epsbeta_z,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2x,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2y,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2z,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cx1,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cy1,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz1,
    torch::PackedTensorAccessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t> PsixD,
    torch::PackedTensorAccessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t> PsiyD,
    torch::PackedTensorAccessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t> PsizD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bxD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> byD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bzD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cxD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cyD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> czD,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> PML_num,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny, const int nz)
{
    // epsbeta是eps_inf+sum(beta)
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies;                    // 对频率数量取模得到频率索引
    if (x >= nx || y >= ny || z >= nz)
        return;

    if (y > 0 && z > 0)
    {
        Ex[source_index][structure_index][x][y][z][frequency_index] =
            (epsbeta_x[structure_index][x][y][z][frequency_index] - sigmadt_2x[structure_index][x][y][z]) * Ex[source_index][structure_index][x][y][z][frequency_index] + Cy1[y] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x][y - 1][z][frequency_index]) - Cz1[z] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x][y][z - 1][frequency_index]);
    }

    if (z > 0 && x > 0)
    {
        Ey[source_index][structure_index][x][y][z][frequency_index] =
            (epsbeta_y[structure_index][x][y][z][frequency_index] - sigmadt_2y[structure_index][x][y][z]) * Ey[source_index][structure_index][x][y][z][frequency_index] + Cz1[z] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y][z - 1][frequency_index]) - Cx1[x] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x - 1][y][z][frequency_index]);
    }

    if (x > 0 && y > 0)
    {
        Ez[source_index][structure_index][x][y][z][frequency_index] =
            (epsbeta_z[structure_index][x][y][z][frequency_index] - sigmadt_2z[structure_index][x][y][z]) * Ez[source_index][structure_index][x][y][z][frequency_index] + Cx1[x] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x - 1][y][z][frequency_index]) - Cy1[y] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y - 1][z][frequency_index]);
    }

    // xPML 更新
    if (x < PML_num[0] && x > 0)
    {
        PsixD[source_index][structure_index][x][y][z][0][frequency_index] =
            bxD[x] * PsixD[source_index][structure_index][x][y][z][0][frequency_index] - cxD[x] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x - 1][y][z][frequency_index]);
        Ey[source_index][structure_index][x][y][z][frequency_index] +=
            PsixD[source_index][structure_index][x][y][z][0][frequency_index];
        PsixD[source_index][structure_index][x][y][z][1][frequency_index] =
            bxD[x] * PsixD[source_index][structure_index][x][y][z][1][frequency_index] + cxD[x] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x - 1][y][z][frequency_index]);
        Ez[source_index][structure_index][x][y][z][frequency_index] +=
            PsixD[source_index][structure_index][x][y][z][1][frequency_index];
    }
    else if (x >= (nx - PML_num[0]))
    {
        uint16_t x0 = x - nx + 2 * PML_num[0];
        PsixD[source_index][structure_index][x0][y][z][0][frequency_index] =
            bxD[x0] * PsixD[source_index][structure_index][x0][y][z][0][frequency_index] - cxD[x0] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x - 1][y][z][frequency_index]);
        Ey[source_index][structure_index][x][y][z][frequency_index] +=
            PsixD[source_index][structure_index][x0][y][z][0][frequency_index];
        PsixD[source_index][structure_index][x0][y][z][1][frequency_index] =
            bxD[x0] * PsixD[source_index][structure_index][x0][y][z][1][frequency_index] + cxD[x0] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x - 1][y][z][frequency_index]);
        Ez[source_index][structure_index][x][y][z][frequency_index] +=
            PsixD[source_index][structure_index][x0][y][z][1][frequency_index];
    }

    // yPML 更新
    if (y < PML_num[1] && y > 0)
    {
        PsiyD[source_index][structure_index][x][y][z][0][frequency_index] =
            byD[y] * PsiyD[source_index][structure_index][x][y][z][0][frequency_index] - cyD[y] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y - 1][z][frequency_index]);
        Ez[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyD[source_index][structure_index][x][y][z][0][frequency_index];
        PsiyD[source_index][structure_index][x][y][z][1][frequency_index] =
            byD[y] * PsiyD[source_index][structure_index][x][y][z][1][frequency_index] + cyD[y] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x][y - 1][z][frequency_index]);
        Ex[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyD[source_index][structure_index][x][y][z][1][frequency_index];
    }
    else if (y >= (ny - PML_num[1]))
    {
        uint16_t y0 = y - ny + 2 * PML_num[1];
        PsiyD[source_index][structure_index][x][y0][z][0][frequency_index] =
            byD[y0] * PsiyD[source_index][structure_index][x][y0][z][0][frequency_index] - cyD[y0] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y - 1][z][frequency_index]);
        Ez[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyD[source_index][structure_index][x][y0][z][0][frequency_index];
        PsiyD[source_index][structure_index][x][y0][z][1][frequency_index] =
            byD[y0] * PsiyD[source_index][structure_index][x][y0][z][1][frequency_index] + cyD[y0] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x][y - 1][z][frequency_index]);
        Ex[source_index][structure_index][x][y][z][frequency_index] +=
            PsiyD[source_index][structure_index][x][y0][z][1][frequency_index];
    }

    // zPML 更新
    if (z < PML_num[2] && z > 0)
    {
        PsizD[source_index][structure_index][x][y][z][0][frequency_index] =
            bzD[z] * PsizD[source_index][structure_index][x][y][z][0][frequency_index] - czD[z] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x][y][z - 1][frequency_index]);
        Ex[source_index][structure_index][x][y][z][frequency_index] +=
            PsizD[source_index][structure_index][x][y][z][0][frequency_index];
        PsizD[source_index][structure_index][x][y][z][1][frequency_index] =
            bzD[z] * PsizD[source_index][structure_index][x][y][z][1][frequency_index] + czD[z] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y][z - 1][frequency_index]);
        Ey[source_index][structure_index][x][y][z][frequency_index] +=
            PsizD[source_index][structure_index][x][y][z][1][frequency_index];
    }
    else if (z >= (nz - PML_num[2]))
    {
        uint16_t z0 = z - nz + 2 * PML_num[2];
        PsizD[source_index][structure_index][x][y][z0][0][frequency_index] =
            bzD[z0] * PsizD[source_index][structure_index][x][y][z0][0][frequency_index] - czD[z0] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x][y][z - 1][frequency_index]);
        Ex[source_index][structure_index][x][y][z][frequency_index] +=
            PsizD[source_index][structure_index][x][y][z0][0][frequency_index];
        PsizD[source_index][structure_index][x][y][z0][1][frequency_index] =
            bzD[z0] * PsizD[source_index][structure_index][x][y][z0][1][frequency_index] + czD[z0] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y][z - 1][frequency_index]);
        Ey[source_index][structure_index][x][y][z][frequency_index] +=
            PsizD[source_index][structure_index][x][y][z0][1][frequency_index];
    }
}

void Update_E(torch::Tensor &Ex, torch::Tensor &Ey, torch::Tensor &Ez, torch::Tensor &Hx, torch::Tensor &Hy, torch::Tensor &Hz,
              torch::Tensor epsbeta_x, torch::Tensor epsbeta_y, torch::Tensor epsbeta_z,
              torch::Tensor sigmadt_2x, torch::Tensor sigmadt_2y, torch::Tensor sigmadt_2z,
              torch::Tensor &Cx1, torch::Tensor &Cy1, torch::Tensor &Cz1, torch::Tensor &PsixD, torch::Tensor &PsiyD, torch::Tensor &PsizD, torch::Tensor &bxD, torch::Tensor &byD, torch::Tensor &bzD, torch::Tensor &cxD, torch::Tensor &cyD, torch::Tensor &czD, torch::Tensor &PML_num, torch::Tensor &Periodic_num)
{
    // 分配线程和块
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int nx = Ex.size(2);
    const int ny = Ey.size(3);
    const int nz = Ez.size(4);
    const int num_frequencies = Ex.size(5);

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    Update_E_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Hx.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Hy.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Hz.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        epsbeta_x.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        epsbeta_y.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        epsbeta_z.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2x.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2y.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2z.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        Cx1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cy1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cz1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PsixD.packed_accessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t>(),
        PsiyD.packed_accessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t>(),
        PsizD.packed_accessor<c10::complex<float>, 7, torch::RestrictPtrTraits, size_t>(),
        bxD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        byD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        bzD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cxD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cyD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        czD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PML_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz);
}

// 这里只是用于还原E,没有色散
// 之所以分成两部,是为了节省内存
__global__ void Update_E_Dispersion_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> epsbeta_x,
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> epsbeta_y,
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> epsbeta_z,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2x,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2y,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2z,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny, const int nz)
{
    // sigma的意义只是在优化中有用,相当于在某个体积分数时,给予pri和sec相等的电导率,所以方程中全都一样,没有实际物理意义
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies;                    // 对频率数量取模得到频率索引

    if (x >= nx || y >= ny || z >= nz)
        return;

    if (y > 0 && z > 0)
    { // x分量
        Ex[source_index][structure_index][x][y][z][frequency_index] =
            Ex[source_index][structure_index][x][y][z][frequency_index] / (epsbeta_x[structure_index][x][y][z][frequency_index] + sigmadt_2x[structure_index][x][y][z]);
    }
    if (z > 0 && x > 0)
    { // y分量
        Ey[source_index][structure_index][x][y][z][frequency_index] =
            Ey[source_index][structure_index][x][y][z][frequency_index] / (epsbeta_y[structure_index][x][y][z][frequency_index] + sigmadt_2y[structure_index][x][y][z]);
    }
    if (x > 0 && y > 0)
    { // z分量
        Ez[source_index][structure_index][x][y][z][frequency_index] =
            Ez[source_index][structure_index][x][y][z][frequency_index] / (epsbeta_z[structure_index][x][y][z][frequency_index] + sigmadt_2z[structure_index][x][y][z]);
    }
}

void Update_E_Dispersion(torch::Tensor Ex, torch::Tensor Ey, torch::Tensor Ez,
                         torch::Tensor epsbeta_x, torch::Tensor epsbeta_y, torch::Tensor epsbeta_z,
                         torch::Tensor sigmadt_2x, torch::Tensor sigmadt_2y, torch::Tensor sigmadt_2z,
                         torch::Tensor Periodic_num)
{
    // 分配线程和块
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int nx = Ex.size(2);
    const int ny = Ey.size(3);
    const int nz = Ez.size(4);
    const int num_frequencies = Ex.size(5);

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    Update_E_Dispersion_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        epsbeta_x.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        epsbeta_y.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        epsbeta_z.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2x.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2y.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2z.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz);
}

// 处理周期性
__global__ void E_boundx(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> x_phase_offset,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> Periodic_num,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny, const int nz, bool isconj)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t y = linear_index / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies;                    // 对频率数量取模得到频率索引

    if (y > ny || z > nz || Periodic_num[0] == 0)
        return;

    if (isconj)
    {
        if (y < ny)
        {
            Ey[source_index][structure_index][0][y][z][frequency_index] =
                Ey[source_index][structure_index][nx - 1][y][z][frequency_index] *
                x_phase_offset[source_index][frequency_index];

            Ey[source_index][structure_index][nx][y][z][frequency_index] =
                Ey[source_index][structure_index][1][y][z][frequency_index] * c10::complex<float>(x_phase_offset[source_index][frequency_index].real(), -x_phase_offset[source_index][frequency_index].imag());
        }
        if (z < nz)
        {
            Ez[source_index][structure_index][0][y][z][frequency_index] =
                Ez[source_index][structure_index][nx - 1][y][z][frequency_index] *
                x_phase_offset[source_index][frequency_index];

            Ez[source_index][structure_index][nx][y][z][frequency_index] =
                Ez[source_index][structure_index][1][y][z][frequency_index] * c10::complex<float>(x_phase_offset[source_index][frequency_index].real(), -x_phase_offset[source_index][frequency_index].imag());
        }
    }
    else
    {
        if (y < ny)
        {
            Ey[source_index][structure_index][0][y][z][frequency_index] =
                Ey[source_index][structure_index][nx - 1][y][z][frequency_index] *
                c10::complex<float>(x_phase_offset[source_index][frequency_index].real(), -x_phase_offset[source_index][frequency_index].imag());

            Ey[source_index][structure_index][nx][y][z][frequency_index] =
                Ey[source_index][structure_index][1][y][z][frequency_index] * x_phase_offset[source_index][frequency_index];
        }
        if (z < nz)
        {
            Ez[source_index][structure_index][0][y][z][frequency_index] =
                Ez[source_index][structure_index][nx - 1][y][z][frequency_index] *
                c10::complex<float>(x_phase_offset[source_index][frequency_index].real(), -x_phase_offset[source_index][frequency_index].imag());

            Ez[source_index][structure_index][nx][y][z][frequency_index] =
                Ez[source_index][structure_index][1][y][z][frequency_index] * x_phase_offset[source_index][frequency_index];
        }
    }
}

__global__ void E_boundy(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> y_phase_offset,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> Periodic_num,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny, const int nz, bool isconj)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies;                    // 对频率数量取模得到频率索引

    if (x > nx || z > nz || Periodic_num[1] == 0)
        return;

    if (isconj)
    {
        if (x < nx)
        {
            Ex[source_index][structure_index][x][0][z][frequency_index] =
                Ex[source_index][structure_index][x][ny - 1][z][frequency_index] *
                y_phase_offset[source_index][frequency_index];

            Ex[source_index][structure_index][x][ny][z][frequency_index] =
                Ex[source_index][structure_index][x][1][z][frequency_index] * c10::complex<float>(y_phase_offset[source_index][frequency_index].real(), -y_phase_offset[source_index][frequency_index].imag());
        }
        if (z < nz)
        {
            Ez[source_index][structure_index][x][0][z][frequency_index] =
                Ez[source_index][structure_index][x][ny - 1][z][frequency_index] *
                y_phase_offset[source_index][frequency_index];

            Ez[source_index][structure_index][x][ny][z][frequency_index] =
                Ez[source_index][structure_index][x][1][z][frequency_index] * c10::complex<float>(y_phase_offset[source_index][frequency_index].real(), -y_phase_offset[source_index][frequency_index].imag());
        }
    }
    else
    {
        if (x < nx)
        {
            Ex[source_index][structure_index][x][0][z][frequency_index] =
                Ex[source_index][structure_index][x][ny - 1][z][frequency_index] *
                c10::complex<float>(y_phase_offset[source_index][frequency_index].real(), -y_phase_offset[source_index][frequency_index].imag());

            Ex[source_index][structure_index][x][ny][z][frequency_index] =
                Ex[source_index][structure_index][x][1][z][frequency_index] * y_phase_offset[source_index][frequency_index];
        }
        if (z < nz)
        {
            Ez[source_index][structure_index][x][0][z][frequency_index] =
                Ez[source_index][structure_index][x][ny - 1][z][frequency_index] *
                c10::complex<float>(y_phase_offset[source_index][frequency_index].real(), -y_phase_offset[source_index][frequency_index].imag());

            Ez[source_index][structure_index][x][ny][z][frequency_index] =
                Ez[source_index][structure_index][x][1][z][frequency_index] * y_phase_offset[source_index][frequency_index];
        }
    }
}

void Update_E_Periodic(torch::Tensor Ex, torch::Tensor Ey, torch::Tensor Ez,
                       torch::Tensor x_phase_offset, torch::Tensor y_phase_offset,
                       torch::Tensor Periodic_num, bool isconj)
{
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int nx = Ex.size(2);
    const int ny = Ey.size(3);
    const int nz = Ez.size(4);
    const int num_frequencies = Ex.size(5);

    const dim3 threads(256, 1, 1);
    const dim3 blockx((ny * nz + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);
    const dim3 blocky((nx * nz + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    E_boundx<<<blockx, threads>>>(
        Ey.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        x_phase_offset.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        Periodic_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz, isconj);

    E_boundy<<<blocky, threads>>>(
        Ex.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        y_phase_offset.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        Periodic_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz, isconj);
}
// 只需要平面光,启动小的线程即可
// 现在是复数光源.只需要输入当前时刻的光就行了,不管它怎么回事
// 始终牢记,实部和虚部是两套系统
__global__ void Inject_H_Plane_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hx,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Hy,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz2,
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Ext,    // (source, time)
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Eyt,    // (source, time)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Ex, // (source, x, y, freq)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Ey, // (source, x, y, freq)
    const torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> delay_map_Ex,         // (x, y), for Hy
    const torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> delay_map_Ey,         // (x, y), for Hx
    const int bound,
    const int PMLx,
    const int PMLy,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny,
    const int nt, const int t_id)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / ny;
    uint16_t y = linear_index % ny;

    if (x >= (nx - PMLx) || y >= (ny - PMLy) || x < PMLx || y < PMLy)
        return;

    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures;
    uint16_t frequency_index = blockIdx.y % num_frequencies;

    // ---- Hx 更新 (基于 Eyt + phi_Ey)，使用 delay_map_Ey
    float delay_Ey = t_id - delay_map_Ey[x][y];
    if (delay_Ey >= 0.0f)
    {
        int t0_Ey = static_cast<int>(floorf(delay_Ey));
        float alpha_Ey = delay_Ey - static_cast<float>(t0_Ey);
        if ((t0_Ey + 1) < nt && x > PMLx)
        {
            c10::complex<float> Eyt_interp = (1.0f - alpha_Ey) * Eyt[source_index][t0_Ey] + alpha_Ey * Eyt[source_index][t0_Ey + 1];
            Hx[source_index][structure_index][x][y][bound][frequency_index] -=
                Cz2[bound] * Eyt_interp * phi_Ey[source_index][x][y][frequency_index];
        }
    }

    // ---- Hy 更新 (基于 Ext + phi_Ex)，使用 delay_map_Ex
    float delay_Ex = t_id - delay_map_Ex[x][y];
    if (delay_Ex >= 0.0f)
    {
        int t0_Ex = static_cast<int>(floorf(delay_Ex));
        float alpha_Ex = delay_Ex - static_cast<float>(t0_Ex);
        if ((t0_Ex + 1) < nt && y > PMLy)
        {
            c10::complex<float> Ext_interp = (1.0f - alpha_Ex) * Ext[source_index][t0_Ex] + alpha_Ex * Ext[source_index][t0_Ex + 1];
            Hy[source_index][structure_index][x][y][bound][frequency_index] +=
                Cz2[bound] * Ext_interp * phi_Ex[source_index][x][y][frequency_index];
        }
    }
}

void Inject_H(
    torch::Tensor &Hx,
    torch::Tensor &Hy,
    torch::Tensor &Cz2,
    torch::Tensor &Ext,
    torch::Tensor &Eyt,
    torch::Tensor &phi_Ex,
    torch::Tensor &phi_Ey,
    torch::Tensor &delay_map_Ex, // ✅ 用于 Hy 注入
    torch::Tensor &delay_map_Ey, // ✅ 用于 Hx 注入
    torch::Tensor &PML_num,
    int bound,
    int t_id)
{
    // 获取维度信息
    const int num_sources = Hx.size(0);
    const int num_structures = Hx.size(1);
    const int num_frequencies = Hx.size(5);
    const int nx = phi_Ex.size(1);
    const int ny = phi_Ey.size(2);
    const int nt = Ext.size(1); // 时间步数

    // 启动核函数
    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny + 255) / 256, num_structures * num_frequencies * num_sources, 1);

    Inject_H_Plane_GPU<<<blocks, threads>>>(
        Hx.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Hy.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Cz2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Ext.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        Eyt.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        phi_Ex.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        phi_Ey.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        delay_map_Ex.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(), // ✅ 用于 Hy
        delay_map_Ey.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(), // ✅ 用于 Hx
        bound,
        PML_num[0].item<int>(),
        PML_num[1].item<int>(),
        num_structures,
        num_frequencies,
        nx, ny,
        nt,
        t_id);
}

__global__ void Inject_E_Plane_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ey,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz1,
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Hxt,    // (source, time)
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Hyt,    // (source, time)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Hx, // (source, x, y, freq)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Hy, // (source, x, y, freq)
    const torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> delay_map_Hx,         // 用于 Ey
    const torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> delay_map_Hy,         // 用于 Ex
    const int bound,
    const int PMLx,
    const int PMLy,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny,
    const int nt, const int t_id)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / ny;
    uint16_t y = linear_index % ny;

    if (x >= (nx - PMLx) || y >= (ny - PMLy) || x < PMLx || y < PMLy)
        return;

    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures;
    uint16_t frequency_index = blockIdx.y % num_frequencies;

    // ---- 更新 Ex：使用 Hyt 和 delay_map_Hy
    float delay_Hy = t_id - delay_map_Hy[x][y];
    if (delay_Hy >= 0.0f)
    {
        int t0_Hy = static_cast<int>(floorf(delay_Hy));
        float alpha_Hy = delay_Hy - static_cast<float>(t0_Hy);
        if ((t0_Hy + 1) < nt && y > PMLy)
        {
            c10::complex<float> Hyt_interp = (1.0f - alpha_Hy) * Hyt[source_index][t0_Hy] + alpha_Hy * Hyt[source_index][t0_Hy + 1];
            Ex[source_index][structure_index][x][y][bound + 1][frequency_index] +=
                Cz1[bound + 1] * Hyt_interp * phi_Hy[source_index][x][y][frequency_index];
        }
    }

    // ---- 更新 Ey：使用 Hxt 和 delay_map_Hx
    float delay_Hx = t_id - delay_map_Hx[x][y];
    if (delay_Hx >= 0.0f)
    {
        int t0_Hx = static_cast<int>(floorf(delay_Hx));
        float alpha_Hx = delay_Hx - static_cast<float>(t0_Hx);
        if ((t0_Hx + 1) < nt && x > PMLx)
        {
            c10::complex<float> Hxt_interp = (1.0f - alpha_Hx) * Hxt[source_index][t0_Hx] + alpha_Hx * Hxt[source_index][t0_Hx + 1];
            Ey[source_index][structure_index][x][y][bound + 1][frequency_index] -=
                Cz1[bound + 1] * Hxt_interp * phi_Hx[source_index][x][y][frequency_index];
        }
    }
}

void Inject_E(
    torch::Tensor &Ex,
    torch::Tensor &Ey,
    torch::Tensor &Cz1,
    torch::Tensor &Hxt,
    torch::Tensor &Hyt,
    torch::Tensor &phi_Hx,
    torch::Tensor &phi_Hy,
    torch::Tensor &delay_map_Hx, // ✅ 新增，用于 Ey 注入
    torch::Tensor &delay_map_Hy, // ✅ 新增，用于 Ex 注入
    torch::Tensor &PML_num,
    int bound, int t_id)
{
    // 获取维度信息
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int num_frequencies = Ex.size(5);
    const int nx = Ex.size(2);
    const int ny = Ey.size(3);
    const int nt = Hxt.size(1); // 时间维度长度

    // CUDA 网格设置
    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny + 255) / 256, num_structures * num_frequencies * num_sources, 1);

    // 调用核函数
    Inject_E_Plane_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Cz1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Hxt.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        Hyt.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        phi_Hx.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        phi_Hy.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        delay_map_Hx.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(), // ✅ 对 Ey 使用
        delay_map_Hy.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(), // ✅ 对 Ex 使用
        bound,
        PML_num[0].item<int>(),
        PML_num[1].item<int>(),
        num_structures,
        num_frequencies,
        nx, ny,
        nt, // ✅ 时间长度
        t_id);
}

__global__ void Inject_J_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ez,
    const torch::PackedTensorAccessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t> Jx,
    const torch::PackedTensorAccessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t> Jy,
    const torch::PackedTensorAccessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t> Jz,
    const int nx_offset, const int ny_offset, const int nz_offset,
    const int num_structures,
    const int num_frequencies,
    const int nx, const int ny, const int nz)
{

    // Derive indices from blockIdx.y
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures;
    uint16_t frequency_index = blockIdx.y % num_frequencies;

    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;

    if (x >= nx || y >= ny || z >= nz)
        return;
    uint16_t xD = x + nx_offset;
    uint16_t yD = y + ny_offset;
    uint16_t zD = z + nz_offset;

    // Apply J to E fields, ensure you handle the indices for multiple dimensions correctly
    if (x < nx)
    {
        Ex[source_index][structure_index][xD][yD][zD][frequency_index] -= Jx[source_index][structure_index][x][y][z];
    }
    if (y < ny)
    {
        Ey[source_index][structure_index][xD][yD][zD][frequency_index] -= Jy[source_index][structure_index][x][y][z];
    }
    if (z < nz)
    {
        Ez[source_index][structure_index][xD][yD][zD][frequency_index] -= Jz[source_index][structure_index][x][y][z];
    }
}

void Inject_J(
    torch::Tensor &Ex,
    torch::Tensor &Ey,
    torch::Tensor &Ez,
    torch::Tensor &Jx,
    torch::Tensor &Jy,
    torch::Tensor &Jz,
    torch::Tensor &n_offset)
{
    // 计算线程和块的维度
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int num_frequencies = Ex.size(5);
    const int nx = Jx.size(2);
    const int ny = Jy.size(3);
    const int nz = Jz.size(4);

    const int nx_offset = n_offset[0].item<int>();
    const int ny_offset = n_offset[1].item<int>();
    const int nz_offset = n_offset[2].item<int>();

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    Inject_J_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Jx.packed_accessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t>(),
        Jy.packed_accessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t>(),
        Jz.packed_accessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t>(),
        nx_offset, ny_offset, nz_offset, num_structures, num_frequencies, nx, ny, nz);
}

/////////////////////////////////////////////////////////添加结构
torch::Tensor get_id_range(const torch::Tensor &x, const torch::Tensor &x_total)
{
    // 初始化id_range
    torch::Tensor id_range = torch::tensor({0, static_cast<int>(x_total.size(0)) - 1}, torch::kInt32);

    // 查找大于x[0]的最小索引
    auto condition1 = (x[0] > x_total).nonzero();
    if (condition1.numel() > 0)
    {
        int idx1 = condition1[-1].item<int>(); // 取最后一个满足条件的索引
        if (idx1 % 2 != 0)                     // 如果是奇数，则向前取一个偶数
        {
            idx1 = std::max(0, idx1 - 1);
        }
        id_range[0] = idx1;
    }

    // 查找小于x[-1]的最大索引
    auto condition2 = (x[-1] < x_total).nonzero();
    if (condition2.numel() > 0)
    {
        int idx2 = condition2[0].item<int>(); // 取第一个满足条件的索引
        if (idx2 % 2 != 0)                    // 如果是奇数，则向后取一个偶数
        {
            idx2 = std::min(static_cast<int>(x_total.size(0)) - 1, idx2 + 1);
        }
        id_range[1] = idx2;
    }

    return id_range;
}

template <typename scalar_t>
__global__ void Mat_Average_GPU(
    torch::PackedTensorAccessor<scalar_t, 4, torch::RestrictPtrTraits, size_t> mat_out, // Updated to 4D
    const torch::PackedTensorAccessor<scalar_t, 1, torch::RestrictPtrTraits, size_t> x2,
    const torch::PackedTensorAccessor<scalar_t, 1, torch::RestrictPtrTraits, size_t> y2,
    const torch::PackedTensorAccessor<scalar_t, 1, torch::RestrictPtrTraits, size_t> z2,
    const torch::PackedTensorAccessor<scalar_t, 4, torch::RestrictPtrTraits, size_t> mat_in, // Updated to 4D
    int x_range_start_id, int y_range_start_id, int z_range_start_id,
    float x_start, float y_start, float z_start,
    float dx, float dy, float dz,
    int nx, int ny, int nz,
    int nxs, int nys, int nzs,
    int nx2, int ny2, int nz2)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int i = linear_index / (ny * nz);
    int j = (linear_index % (ny * nz)) / nz;
    int k = linear_index % nz;

    int p = blockIdx.y; // Parallel dimension index

    if (i >= nx || j >= ny || k >= nz)
        return; // Check bounds

    int x_out = i + x_range_start_id;
    int y_out = j + y_range_start_id;
    int z_out = k + z_range_start_id;

    float x2_before, x2_after, y2_before, y2_after, z2_before, z2_after;

    x2_before = (x_out <= 0) ? x2[0] : (x2[x_out - 1] + x2[x_out]) / 2;
    x2_after = (x_out >= nx2 - 1) ? x2[nx2 - 1] : (x2[x_out + 1] + x2[x_out]) / 2;

    y2_before = (y_out <= 0) ? y2[0] : (y2[y_out - 1] + y2[y_out]) / 2;
    y2_after = (y_out >= ny2 - 1) ? y2[ny2 - 1] : (y2[y_out + 1] + y2[y_out]) / 2;

    z2_before = (z_out <= 0) ? z2[0] : (z2[z_out - 1] + z2[z_out]) / 2;
    z2_after = (z_out >= nz2 - 1) ? z2[nz2 - 1] : (z2[z_out + 1] + z2[z_out]) / 2;

    float dV = (x2_after - x2_before) * (y2_after - y2_before) * (z2_after - z2_before);

    int x_start_local_id = floor((x2_before - x_start) / dx);
    int x_end_local_id = floor((x2_after - x_start) / dx);

    int y_start_local_id = floor((y2_before - y_start) / dy);
    int y_end_local_id = floor((y2_after - y_start) / dy);

    int z_start_local_id = floor((z2_before - z_start) / dz);
    int z_end_local_id = floor((z2_after - z_start) / dz);

    float xb_start, xb_end, yb_start, yb_end, zb_start, zb_end;
    float temp = 0;

    for (int x = x_start_local_id; x <= x_end_local_id; ++x)
    {
        xb_start = (x == x_start_local_id) ? x2_before : x * dx + x_start;
        xb_end = (x == x_end_local_id) ? x2_after : (x + 1) * dx + x_start;

        for (int y = y_start_local_id; y <= y_end_local_id; ++y)
        {
            yb_start = (y == y_start_local_id) ? y2_before : y * dy + y_start;
            yb_end = (y == y_end_local_id) ? y2_after : (y + 1) * dy + y_start;

            for (int z = z_start_local_id; z <= z_end_local_id; ++z)
            {
                zb_start = (z == z_start_local_id) ? z2_before : z * dz + z_start;
                zb_end = (z == z_end_local_id) ? z2_after : (z + 1) * dz + z_start;

                if (x >= 0 && y >= 0 && z >= 0 && x < nxs && y < nys && z < nzs)
                {
                    temp += mat_in[p][x][y][z] * (xb_end - xb_start) * (yb_end - yb_start) * (zb_end - zb_start) / dV;
                }
            }
        }
    }
    mat_out[p][i][j][k] = temp;
}

std::tuple<torch::Tensor, torch::Tensor, torch::Tensor, torch::Tensor> Mat_average(
    const torch::Tensor &x_range,
    const torch::Tensor &y_range,
    const torch::Tensor &z_range,
    const torch::Tensor &mat_in, // 已假设包含并行维度
    const torch::Tensor &x2,
    const torch::Tensor &y2,
    const torch::Tensor &z2)
{
    if (!torch::cuda::is_available())
    {
        throw std::runtime_error("Error: CUDA not available.");
    }
    if (mat_in.device().type() != torch::kCUDA || x2.device().type() != torch::kCUDA || y2.device().type() != torch::kCUDA || z2.device().type() != torch::kCUDA)
    {
        throw std::runtime_error("Error: Tensor is not on GPU.");
    }

    auto x_range_id = get_id_range(x_range, x2);
    auto y_range_id = get_id_range(y_range, y2);
    auto z_range_id = get_id_range(z_range, z2);

    int np = mat_in.size(0); // Parallel dimension size
    int nxs = mat_in.size(1);
    int nys = mat_in.size(2);
    int nzs = mat_in.size(3);
    int nx2 = x2.size(0);
    int ny2 = y2.size(0);
    int nz2 = z2.size(0);
    int nx = x_range_id[1].item<int>() - x_range_id[0].item<int>() + 1;
    int ny = y_range_id[1].item<int>() - y_range_id[0].item<int>() + 1;
    int nz = z_range_id[1].item<int>() - z_range_id[0].item<int>() + 1;

    torch::Tensor mat_out = torch::zeros({np, nx, ny, nz}).to(torch::kCUDA);

    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny * nz + 256 - 1) / 256, np, 1); // Updated to include parallel dimension

    AT_DISPATCH_FLOATING_TYPES(mat_out.scalar_type(), "Mat_Average_GPU", ([&]
                                                                          { Mat_Average_GPU<<<blocks, threads>>>(
                                                                                mat_out.packed_accessor<scalar_t, 4, torch::RestrictPtrTraits, size_t>(), // Updated to 4D
                                                                                x2.packed_accessor<scalar_t, 1, torch::RestrictPtrTraits, size_t>(),
                                                                                y2.packed_accessor<scalar_t, 1, torch::RestrictPtrTraits, size_t>(),
                                                                                z2.packed_accessor<scalar_t, 1, torch::RestrictPtrTraits, size_t>(),
                                                                                mat_in.packed_accessor<scalar_t, 4, torch::RestrictPtrTraits, size_t>(), // Updated to 4D
                                                                                x_range_id[0].item<int>(), y_range_id[0].item<int>(), z_range_id[0].item<int>(),
                                                                                x_range[0].item<float>(), y_range[0].item<float>(), z_range[0].item<float>(),
                                                                                ((x_range[1] - x_range[0]) / nxs).item<float>(),
                                                                                ((y_range[1] - y_range[0]) / nys).item<float>(),
                                                                                ((z_range[1] - z_range[0]) / nzs).item<float>(),
                                                                                nx, ny, nz,
                                                                                nxs, nys, nzs,
                                                                                nx2, ny2, nz2); }));

    cudaDeviceSynchronize();
    return std::make_tuple(mat_out, x_range_id, y_range_id, z_range_id);
}

// 设置weight和mat
__global__ void Set_weight_mat_id_GPU( // 最先执行,根据总平均密度修改pri和sec
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z2,
    const torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> mat_in, // (结构并行,x,y,z)
    const int pri_id,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weight,   //(p,x,y,z)
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_id_mat, //(p,x,y,z)
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_id_mat, //(p,x,y,z)
    int x_range_start_id, int y_range_start_id, int z_range_start_id,
    float x_start, float y_start, float z_start,
    float dx, float dy, float dz,
    int nx, int ny, int nz,
    int nxs, int nys, int nzs,
    int nx2, int ny2, int nz2)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int i = linear_index / (ny * nz);
    int j = (linear_index % (ny * nz)) / nz;
    int k = linear_index % nz;

    int p = blockIdx.y; // 结构索引

    if (i >= nx || j >= ny || k >= nz)
        return; // Check bounds

    int x_out = i + x_range_start_id;
    int y_out = j + y_range_start_id;
    int z_out = k + z_range_start_id;

    float x2_before, x2_after, y2_before, y2_after, z2_before, z2_after;

    x2_before = (x_out <= 0) ? x2[0] : (x2[x_out - 1] + x2[x_out]) / 2;
    x2_after = (x_out >= nx2 - 1) ? x2[nx2 - 1] : (x2[x_out + 1] + x2[x_out]) / 2;

    y2_before = (y_out <= 0) ? y2[0] : (y2[y_out - 1] + y2[y_out]) / 2;
    y2_after = (y_out >= ny2 - 1) ? y2[ny2 - 1] : (y2[y_out + 1] + y2[y_out]) / 2;

    z2_before = (z_out <= 0) ? z2[0] : (z2[z_out - 1] + z2[z_out]) / 2;
    z2_after = (z_out >= nz2 - 1) ? z2[nz2 - 1] : (z2[z_out + 1] + z2[z_out]) / 2;

    float dV = (x2_after - x2_before) * (y2_after - y2_before) * (z2_after - z2_before);

    int x_start_local_id = floor((x2_before - x_start) / dx);
    int x_end_local_id = floor((x2_after - x_start) / dx);

    int y_start_local_id = floor((y2_before - y_start) / dy);
    int y_end_local_id = floor((y2_after - y_start) / dy);

    int z_start_local_id = floor((z2_before - z_start) / dz);
    int z_end_local_id = floor((z2_after - z_start) / dz);

    float xb_start, xb_end, yb_start, yb_end, zb_start, zb_end;
    float weight = 0; // weight是总平均密度

    for (int x = x_start_local_id; x <= x_end_local_id; ++x)
    {
        xb_start = (x == x_start_local_id) ? x2_before : x * dx + x_start;
        xb_end = (x == x_end_local_id) ? x2_after : (x + 1) * dx + x_start;

        for (int y = y_start_local_id; y <= y_end_local_id; ++y)
        {
            yb_start = (y == y_start_local_id) ? y2_before : y * dy + y_start;
            yb_end = (y == y_end_local_id) ? y2_after : (y + 1) * dy + y_start;

            for (int z = z_start_local_id; z <= z_end_local_id; ++z)
            {
                zb_start = (z == z_start_local_id) ? z2_before : z * dz + z_start;
                zb_end = (z == z_end_local_id) ? z2_after : (z + 1) * dz + z_start;

                if (x >= 0 && y >= 0 && z >= 0 && x < nxs && y < nys && z < nzs)
                {
                    weight += (xb_end - xb_start) * (yb_end - yb_start) * (zb_end - zb_start) / dV * mat_in[p][x][y][z];
                }
            }
        }
    }

    // 采用优先级,如果体积比等于0,则不变
    if (weight > 0)
    { // 若体积比大于等于pri,则修改pri=体积比,sec_mat_id=pri_mat_id,pri_mat_id=pri_id.
        sec_id_mat[p][x_out][y_out][z_out] = pri_id_mat[p][x_out][y_out][z_out];
        pri_id_mat[p][x_out][y_out][z_out] = pri_id;
        pri_weight[p][x_out][y_out][z_out] = weight;
    }
}

void Set_weight_mat_id(const torch::Tensor &x_range, const torch::Tensor &y_range, const torch::Tensor &z_range, const torch::Tensor &mat_in, const torch::Tensor &x2, const torch::Tensor &y2, const torch::Tensor &z2, int pri_id, torch::Tensor pri_weight, torch::Tensor pri_id_mat, torch::Tensor sec_id_mat)
{
    // 计算平均占比
    if (!torch::cuda::is_available())
    {
        throw std::runtime_error("Error: CUDA not available.");
    }
    if (mat_in.device().type() != torch::kCUDA || x2.device().type() != torch::kCUDA || y2.device().type() != torch::kCUDA || z2.device().type() != torch::kCUDA)
    {
        throw std::runtime_error("Error: Tensor is not on GPU.");
    }
    auto x_range_id = get_id_range(x_range, x2);
    auto y_range_id = get_id_range(y_range, y2);
    auto z_range_id = get_id_range(z_range, z2);

    int nx, ny, nz, nxs, nys, nzs, nx2, ny2, nz2;
    nx = x_range_id[1].item<int>() - x_range_id[0].item<int>() + 1;
    ny = y_range_id[1].item<int>() - y_range_id[0].item<int>() + 1;
    nz = z_range_id[1].item<int>() - z_range_id[0].item<int>() + 1;

    int np = mat_in.size(0); // Parallel dimension size
    nxs = mat_in.size(1);
    nys = mat_in.size(2);
    nzs = mat_in.size(3);
    nx2 = x2.size(0);
    ny2 = y2.size(0);
    nz2 = z2.size(0);

    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny * nz + 256 - 1) / 256, np, 1);
    Set_weight_mat_id_GPU<<<blocks, threads>>>(
        x2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        mat_in.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_id,
        pri_weight.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        x_range_id[0].item<int>(), y_range_id[0].item<int>(), z_range_id[0].item<int>(),
        x_range[0].item<float>(), y_range[0].item<float>(), z_range[0].item<float>(),
        ((x_range[1] - x_range[0]) / nxs).item<float>(), ((y_range[1] - y_range[0]) / nys).item<float>(), ((z_range[1] - z_range[0]) / nzs).item<float>(),
        nx, ny, nz,
        nxs, nys, nzs,
        nx2, ny2, nz2);
}

// 根据weight和mat获得体积平均ER
__global__ void Set_ER_average_GPU(                                                             // 单纯的根据pri_weight,pri_id_mat和sec_id_mat设置ER
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> ER,                 // (结构并行,x,y,z,波长)
    const torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weight,   //(p,x,y,z)
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> er_list,      //(材料数目,波长,只支持实数)
    const int num_frequencies,
    int nx, int ny, int nz)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int i = linear_index / (ny * nz);
    int j = (linear_index % (ny * nz)) / nz;
    int k = linear_index % nz;

    int p = blockIdx.y / num_frequencies;               // 结构索引
    int frequency_index = blockIdx.y % num_frequencies; // 波长索引

    if (i >= nx || j >= ny || k >= nz)
        return; // Check bounds
    ER[p][i][j][k][frequency_index] = pri_weight[p][i][j][k] * er_list[pri_id_mat[p][i][j][k]][frequency_index] + (1 - pri_weight[p][i][j][k]) * er_list[sec_id_mat[p][i][j][k]][frequency_index];
}

void Set_ER_average(torch::Tensor ER, torch::Tensor pri_weight, torch::Tensor pri_id_mat, torch::Tensor sec_id_mat, torch::Tensor er_list)
{
    int nx, ny, nz;
    nx = ER.size(1);
    ny = ER.size(2);
    nz = ER.size(3);
    int np = ER.size(0);      // Parallel dimension size
    int nf = er_list.size(1); // Parallel dimension size
    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny * nz + 256 - 1) / 256, np * nf, 1);
    Set_ER_average_GPU<<<blocks, threads>>>(
        ER.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        pri_weight.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        er_list.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(),
        nf,
        nx, ny, nz);
}

__global__ void Set_ER_subcell_GPU(
    torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> ER,      // (结构并行,x,y,z,波长)
    const torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> N, // (结构并行,x,y,z,分量)
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z2,
    const torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> mat_in, // (结构并行,x,y,z)
    const int pri_id,
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> er_list,      //(材料数目,波长,只支持实数)
    const int dim,                                                                              // 维度
    const int num_frequencies,
    int x_range_start_id, int y_range_start_id, int z_range_start_id,
    float x_start, float y_start, float z_start,
    float dx, float dy, float dz,
    int nx, int ny, int nz,
    int nxs, int nys, int nzs,
    int nx2, int ny2, int nz2)
{
    // 根据平均值,倒数平均值和法向量计算等效介电常数
    // 注意了现在直接在整个ER上做修改!!!!!!!!!!!!!
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int i = linear_index / (ny * nz);
    int j = (linear_index % (ny * nz)) / nz;
    int k = linear_index % nz;

    int p = blockIdx.y / num_frequencies;               // 结构索引
    int frequency_index = blockIdx.y % num_frequencies; // 波长索引

    if (i >= nx || j >= ny || k >= nz)
        return; // Check bounds

    int x_out = i + x_range_start_id;
    int y_out = j + y_range_start_id;
    int z_out = k + z_range_start_id;

    if (pri_id != pri_id_mat[p][x_out][y_out][z_out])
        return;

    // 如果两个材料的er都大于0才能用子像素平滑,否则还是用最近邻插值
    if (er_list[pri_id_mat[p][x_out][y_out][z_out]][frequency_index] < 0 || er_list[sec_id_mat[p][x_out][y_out][z_out]][frequency_index] < 0)
    {
        ER[p][x_out][y_out][z_out][frequency_index] = er_list[pri_id_mat[p][x_out][y_out][z_out]][frequency_index];
        return;
    }

    float x2_before, x2_after, y2_before, y2_after, z2_before, z2_after;

    x2_before = (x_out <= 0) ? x2[0] : (x2[x_out - 1] + x2[x_out]) / 2;
    x2_after = (x_out >= nx2 - 1) ? x2[nx2 - 1] : (x2[x_out + 1] + x2[x_out]) / 2;

    y2_before = (y_out <= 0) ? y2[0] : (y2[y_out - 1] + y2[y_out]) / 2;
    y2_after = (y_out >= ny2 - 1) ? y2[ny2 - 1] : (y2[y_out + 1] + y2[y_out]) / 2;

    z2_before = (z_out <= 0) ? z2[0] : (z2[z_out - 1] + z2[z_out]) / 2;
    z2_after = (z_out >= nz2 - 1) ? z2[nz2 - 1] : (z2[z_out + 1] + z2[z_out]) / 2;

    float dV = (x2_after - x2_before) * (y2_after - y2_before) * (z2_after - z2_before);

    int x_start_local_id = floor((x2_before - x_start) / dx);
    int x_end_local_id = floor((x2_after - x_start) / dx);

    int y_start_local_id = floor((y2_before - y_start) / dy);
    int y_end_local_id = floor((y2_after - y_start) / dy);

    int z_start_local_id = floor((z2_before - z_start) / dz);
    int z_end_local_id = floor((z2_after - z_start) / dz);

    float xb_start, xb_end, yb_start, yb_end, zb_start, zb_end;
    float weight = 0, total_weight = 0, F = 0, Reciprocal_average = 0; // weight是体积分数,total_weight是总体积分数,基本为1,但是在边缘不为1,用于补偿sec_mat.F是ER的平均值,Reciprocal_average是倒数平均值.

    for (int x = x_start_local_id; x <= x_end_local_id; ++x)
    {
        xb_start = (x == x_start_local_id) ? x2_before : x * dx + x_start;
        xb_end = (x == x_end_local_id) ? x2_after : (x + 1) * dx + x_start;

        for (int y = y_start_local_id; y <= y_end_local_id; ++y)
        {
            yb_start = (y == y_start_local_id) ? y2_before : y * dy + y_start;
            yb_end = (y == y_end_local_id) ? y2_after : (y + 1) * dy + y_start;

            for (int z = z_start_local_id; z <= z_end_local_id; ++z)
            {
                zb_start = (z == z_start_local_id) ? z2_before : z * dz + z_start;
                zb_end = (z == z_end_local_id) ? z2_after : (z + 1) * dz + z_start;

                if (x >= 0 && y >= 0 && z >= 0 && x < nxs && y < nys && z < nzs)
                {
                    weight = (xb_end - xb_start) * (yb_end - yb_start) * (zb_end - zb_start) / dV;
                    total_weight += weight;

                    F += weight * (mat_in[p][x][y][z] * er_list[pri_id][frequency_index] + (1 - mat_in[p][x][y][z]) * er_list[sec_id_mat[p][x_out][y_out][z_out]][frequency_index]);

                    Reciprocal_average += weight / (mat_in[p][x][y][z] * er_list[pri_id][frequency_index] + (1 - mat_in[p][x][y][z]) * er_list[sec_id_mat[p][x_out][y_out][z_out]][frequency_index]);
                }
            }
        }
    }

    F += (1 - total_weight) * er_list[sec_id_mat[p][x_out][y_out][z_out]][frequency_index];
    Reciprocal_average += (1 - total_weight) / er_list[sec_id_mat[p][x_out][y_out][z_out]][frequency_index];

    // 如果两个材料的er都大于0才能用子像素平滑,否则还是用最近邻插值
    if (dim == 0)
    {
        ER[p][x_out][y_out][z_out][frequency_index] = 1 / (N[p][x_out][y_out][z_out][0] * N[p][x_out][y_out][z_out][0] * Reciprocal_average + (1 - N[p][x_out][y_out][z_out][0] * N[p][x_out][y_out][z_out][0]) / F);
    }
    else if (dim == 1)
    {
        ER[p][x_out][y_out][z_out][frequency_index] = 1 / (N[p][x_out][y_out][z_out][1] * N[p][x_out][y_out][z_out][1] * Reciprocal_average + (1 - N[p][x_out][y_out][z_out][1] * N[p][x_out][y_out][z_out][1]) / F);
    }
    else
    {
        ER[p][x_out][y_out][z_out][frequency_index] = 1 / (N[p][x_out][y_out][z_out][2] * N[p][x_out][y_out][z_out][2] * Reciprocal_average + (1 - N[p][x_out][y_out][z_out][2] * N[p][x_out][y_out][z_out][2]) / F);
    }
}

std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> Set_ER_subcell(const torch::Tensor &x_range, const torch::Tensor &y_range, const torch::Tensor &z_range, const torch::Tensor &mat_in, const torch::Tensor &x2, const torch::Tensor &y2, const torch::Tensor &z2, torch::Tensor ER, int pri_id, torch::Tensor pri_id_mat, torch::Tensor sec_id_mat, torch::Tensor N, const torch::Tensor er_list, int dim)
{
    // 新的用于平滑介电常数的,和get_id_range是一对,无限制
    // 直接通过Set_ER,修改pri_mat_id,sec_mat_id和ER,现在只需要返回修改的范围
    // 如果体积分数大于等于0.5,则sec=pri,pri=新的,ER=加权和
    // 如果体积分数小于0.5,则sec=新的,ER=加权和.
    // ER(结构并行,x,y,z,频率)
    // sec_id_mat(结构并行,x,y,z)
    if (!torch::cuda::is_available())
    {
        throw std::runtime_error("Error: CUDA not available.");
    }
    if (mat_in.device().type() != torch::kCUDA || x2.device().type() != torch::kCUDA || y2.device().type() != torch::kCUDA || z2.device().type() != torch::kCUDA)
    {
        throw std::runtime_error("Error: Tensor is not on GPU.");
    }

    auto x_range_id = get_id_range(x_range, x2);
    auto y_range_id = get_id_range(y_range, y2);
    auto z_range_id = get_id_range(z_range, z2);

    int nx, ny, nz, nxs, nys, nzs, nx2, ny2, nz2;
    nx = x_range_id[1].item<int>() - x_range_id[0].item<int>() + 1;
    ny = y_range_id[1].item<int>() - y_range_id[0].item<int>() + 1;
    nz = z_range_id[1].item<int>() - z_range_id[0].item<int>() + 1;

    int np = mat_in.size(0);  // Parallel dimension size
    int nf = er_list.size(1); // Parallel dimension size
    nxs = mat_in.size(1);
    nys = mat_in.size(2);
    nzs = mat_in.size(3);
    nx2 = x2.size(0);
    ny2 = y2.size(0);
    nz2 = z2.size(0);

    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny * nz + 256 - 1) / 256, np * nf, 1);
    ///////////////////////////////还没写呢
    Set_ER_subcell_GPU<<<blocks, threads>>>(
        ER.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        N.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        x2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        mat_in.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_id,
        pri_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        er_list.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(),
        dim,
        nf,
        x_range_id[0].item<int>(), y_range_id[0].item<int>(), z_range_id[0].item<int>(),
        x_range[0].item<float>(), y_range[0].item<float>(), z_range[0].item<float>(),
        ((x_range[1] - x_range[0]) / nxs).item<float>(), ((y_range[1] - y_range[0]) / nys).item<float>(), ((z_range[1] - z_range[0]) / nzs).item<float>(),
        nx, ny, nz,
        nxs, nys, nzs,
        nx2, ny2, nz2);

    return std::make_tuple(x_range_id, y_range_id, z_range_id);
}

////////////////////////////////////////////////监视器值
__global__ void Monitor_Update_GPU_E(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Exw,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Eyw,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> Ezw,
    const torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    const torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    const torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    const torch::PackedTensorAccessor<c10::complex<float>, 1, torch::RestrictPtrTraits, size_t> kernel,
    int x_range_start_id, int y_range_start_id, int z_range_start_id,
    const int num_structures,
    const int num_frequencies,
    int nxb, int nyb, int nzb)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int i = linear_index / (nyb * nzb);
    int j = (linear_index % (nyb * nzb)) / nzb;
    int k = linear_index % nzb;
    int source_index = blockIdx.y / (num_structures * num_frequencies);    // 先除以结构和频率的总数得到源索引
    int structure_index = (blockIdx.y / num_frequencies) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    int frequency_index = blockIdx.y % num_frequencies;                    // 对频率数量取模得到频率索引

    if (i >= nxb || j >= nyb || k >= nzb)
        return; // Check bounds

    int x = i + x_range_start_id;
    int y = j + y_range_start_id;
    int z = k + z_range_start_id;

    if (i < nxb - 1)
    {
        Exw[source_index][structure_index][i][j][k][frequency_index] += kernel[frequency_index] * Ex[source_index][structure_index][x][y][z][frequency_index];
    }
    if (j < nyb - 1)
    {
        Eyw[source_index][structure_index][i][j][k][frequency_index] += kernel[frequency_index] * Ey[source_index][structure_index][x][y][z][frequency_index];
    }
    if (k < nzb - 1)
    {
        Ezw[source_index][structure_index][i][j][k][frequency_index] += kernel[frequency_index] * Ez[source_index][structure_index][x][y][z][frequency_index];
    }
}

torch::Tensor get_id(torch::Tensor xi, torch::Tensor x, bool nearest = false)
{
    // 确保输入是一维的并且在相同的设备上
    xi = xi.unsqueeze(1); // 将xi变为列向量
    x = x.unsqueeze(0);   // 将x变为行向量

    // 计算差异矩阵
    auto diffs = xi - x;

    if (nearest)
    {
        // 如果是最近邻搜索，则取绝对值
        diffs = torch::abs(diffs);
        // 找到最小值的索引
        auto id = torch::argmin(diffs, 1).to(torch::kInt32);

        // // 修正边界情况
        // id = torch::clamp(id, 1, x.size(1) - 2);

        return id.to(torch::kInt32);
    }
    else
    {
        // 向下取整，将正数差异转换为0，负数差异转换为1，以便找到最后一个负数差异的位置
        diffs = (diffs < 0).to(torch::kFloat32);

        // 找到最大值的索引，即最后一个负数差异的位置
        auto id = torch::argmax(diffs, 1) - 1;

        // 修正边界情况
        id = torch::clamp(id, 0, x.size(1) - 2);

        return id.to(torch::kInt32);
    }
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
    m.def("Update_E_Dispersion", &Update_E_Dispersion, "Update_E_Dispersion");
    m.def("Update_H", &Update_H, "Update_H");
    m.def("Update_E", &Update_E, "Update_E");
    m.def("Inject_H", &Inject_H, "Inject_H");
    m.def("Inject_E", &Inject_E, "Inject_E");
    m.def("Inject_J", &Inject_J, "Inject_J");
    m.def("get_id_range", &get_id_range, "get_id_range");
    m.def("Mat_average", &Mat_average, "Average sampling for index");
    m.def("Set_weight_mat_id", &Set_weight_mat_id, "Set_weight_mat_id");
    m.def("Set_ER_average", &Set_ER_average, "Set_ER_average");
    m.def("Set_ER_subcell", &Set_ER_subcell, "Set_ER_subcell");
    m.def("Update_E_Periodic", &Update_E_Periodic, "Update_E_Periodic");
}
