//  这个应该是最终核心求解器版本了.
//  第一个是光源并行维度,针对不同的偏振,入射角并行.
//  第二个是结构并行维度,针对不同的结构并行,用于鲁棒性/结构扫描
//  最后一个维度是频率*2的并行维度,一般只有bloch边界需要(频率1,频率2,频率1虚,频率2虚)
//  后续的测试,包括bloch,子像素平滑精度测试,多体并行
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
__global__ void Update_H_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hx,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hy,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hz,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cx2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cy2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz2,
    torch::PackedTensorAccessor<float, 7, torch::RestrictPtrTraits, size_t> PsixH,
    torch::PackedTensorAccessor<float, 7, torch::RestrictPtrTraits, size_t> PsiyH,
    torch::PackedTensorAccessor<float, 7, torch::RestrictPtrTraits, size_t> PsizH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bxH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> byH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bzH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cxH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cyH,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> czH,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> PML_num,
    const int num_structures,
    const int num_frequencies2,
    const int nx, const int ny, const int nz)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies2);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies2) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies2;                    // 对频率数量取模得到频率索引

    if (x >= nx || y >= ny || z >= nz)
        return;

    Hx[source_index][structure_index][x][y][z][frequency_index] +=
        Cz2[z] * (Ey[source_index][structure_index][x][y][z + 1][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]) - Cy2[y] * (Ez[source_index][structure_index][x][y + 1][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]);
    Hy[source_index][structure_index][x][y][z][frequency_index] +=
        Cx2[x] * (Ez[source_index][structure_index][x + 1][y][z][frequency_index] - Ez[source_index][structure_index][x][y][z][frequency_index]) - Cz2[z] * (Ex[source_index][structure_index][x][y][z + 1][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]);
    Hz[source_index][structure_index][x][y][z][frequency_index] +=
        Cy2[y] * (Ex[source_index][structure_index][x][y + 1][z][frequency_index] - Ex[source_index][structure_index][x][y][z][frequency_index]) - Cx2[x] * (Ey[source_index][structure_index][x + 1][y][z][frequency_index] - Ey[source_index][structure_index][x][y][z][frequency_index]);

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
    const int num_frequencies2 = Ex.size(5);

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies2, 1);

    Update_H_GPU<<<blocks, threads>>>(
        Hx.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Hy.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Hz.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Cx2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cy2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cz2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PsixH.packed_accessor<float, 7, torch::RestrictPtrTraits, size_t>(),
        PsiyH.packed_accessor<float, 7, torch::RestrictPtrTraits, size_t>(),
        PsizH.packed_accessor<float, 7, torch::RestrictPtrTraits, size_t>(),
        bxH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        byH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        bzH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cxH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cyH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        czH.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PML_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies2,
        nx, ny, nz);
}

__global__ void Update_E_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hx,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hy,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hz,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta_x,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta_y,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta_z,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2x,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2y,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2z,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cx1,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cy1,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz1,
    torch::PackedTensorAccessor<float, 7, torch::RestrictPtrTraits, size_t> PsixD,
    torch::PackedTensorAccessor<float, 7, torch::RestrictPtrTraits, size_t> PsiyD,
    torch::PackedTensorAccessor<float, 7, torch::RestrictPtrTraits, size_t> PsizD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bxD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> byD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> bzD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cxD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> cyD,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> czD,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> PML_num,
    const int num_structures,
    const int num_frequencies2,
    const int nx, const int ny, const int nz)
{
    // epsbeta是eps_inf+sum(beta)
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies2);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies2) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies2;                    // 对频率数量取模得到频率索引
    if (x >= nx || y >= ny || z >= nz)
        return;

    if (y > 0 && z > 0)
    {
        Ex[source_index][structure_index][x][y][z][frequency_index] =
            (epsbeta_x[structure_index][x][y][z] - sigmadt_2x[structure_index][x][y][z]) * Ex[source_index][structure_index][x][y][z][frequency_index] + Cy1[y] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x][y - 1][z][frequency_index]) - Cz1[z] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x][y][z - 1][frequency_index]);
    }

    if (z > 0 && x > 0)
    {
        Ey[source_index][structure_index][x][y][z][frequency_index] =
            (epsbeta_y[structure_index][x][y][z] - sigmadt_2y[structure_index][x][y][z]) * Ey[source_index][structure_index][x][y][z][frequency_index] + Cz1[z] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y][z - 1][frequency_index]) - Cx1[x] * (Hz[source_index][structure_index][x][y][z][frequency_index] - Hz[source_index][structure_index][x - 1][y][z][frequency_index]);
    }

    if (x > 0 && y > 0)
    {
        Ez[source_index][structure_index][x][y][z][frequency_index] =
            (epsbeta_z[structure_index][x][y][z] - sigmadt_2z[structure_index][x][y][z]) * Ez[source_index][structure_index][x][y][z][frequency_index] + Cx1[x] * (Hy[source_index][structure_index][x][y][z][frequency_index] - Hy[source_index][structure_index][x - 1][y][z][frequency_index]) - Cy1[y] * (Hx[source_index][structure_index][x][y][z][frequency_index] - Hx[source_index][structure_index][x][y - 1][z][frequency_index]);
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
    const int num_frequencies2 = Ex.size(5);

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies2, 1);

    Update_E_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Hx.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Hy.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Hz.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        epsbeta_x.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        epsbeta_y.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        epsbeta_z.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2x.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2y.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2z.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        Cx1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cy1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Cz1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PsixD.packed_accessor<float, 7, torch::RestrictPtrTraits, size_t>(),
        PsiyD.packed_accessor<float, 7, torch::RestrictPtrTraits, size_t>(),
        PsizD.packed_accessor<float, 7, torch::RestrictPtrTraits, size_t>(),
        bxD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        byD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        bzD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cxD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        cyD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        czD.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        PML_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies2,
        nx, ny, nz);
}

__global__ void Update_E_Dispersion_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex_1,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey_1,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez_1,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weightx,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weighty,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weightz,
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_mat_idx,
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_mat_idy,
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_mat_idz,
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_mat_idx,
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_mat_idy,
    torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_mat_idz,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta_x,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta_y,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta_z,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2x,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2y,
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> sigmadt_2z,
    const torch::PackedTensorAccessor<c10::complex<float>, 1, torch::RestrictPtrTraits, size_t> kp_list, // m
    const torch::PackedTensorAccessor<c10::complex<float>, 1, torch::RestrictPtrTraits, size_t> bp_list, // m
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> pri_Jpdtx,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> pri_Jpdty,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> pri_Jpdtz,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> sec_Jpdtx,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> sec_Jpdty,
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> sec_Jpdtz,
    const int num_structures,
    const int num_frequencies2,
    const int nx, const int ny, const int nz)
{
    // sigma的意义只是在优化中有用,相当于在某个体积分数时,给予pri和sec相等的电导率,所以方程中全都一样,没有实际物理意义
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / (ny * nz);
    uint16_t y = (linear_index % (ny * nz)) / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies2);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies2) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t frequency_index = blockIdx.y % num_frequencies2;                    // 对频率数量取模得到频率索引

    if (x >= nx || y >= ny || z >= nz)
        return;

    if (y > 0 && z > 0)
    { // x分量
        Ex[source_index][structure_index][x][y][z][frequency_index] = (Ex[source_index][structure_index][x][y][z][frequency_index] - ((1 + kp_list[pri_mat_idx[structure_index][x][y][z]]) * pri_Jpdtx[source_index][structure_index][x][y][z][frequency_index]).real() - ((1 + kp_list[sec_mat_idx[structure_index][x][y][z]]) * sec_Jpdtx[source_index][structure_index][x][y][z][frequency_index]).real()) / (epsbeta_x[structure_index][x][y][z] + sigmadt_2x[structure_index][x][y][z]);

        pri_Jpdtx[source_index][structure_index][x][y][z][frequency_index] =
            kp_list[pri_mat_idx[structure_index][x][y][z]] *
                pri_Jpdtx[source_index][structure_index][x][y][z][frequency_index] +
            pri_weightx[structure_index][x][y][z] * bp_list[pri_mat_idx[structure_index][x][y][z]] *
                (Ex[source_index][structure_index][x][y][z][frequency_index] - Ex_1[source_index][structure_index][x][y][z][frequency_index]);
        sec_Jpdtx[source_index][structure_index][x][y][z][frequency_index] =
            kp_list[sec_mat_idx[structure_index][x][y][z]] * sec_Jpdtx[source_index][structure_index][x][y][z][frequency_index] +
            (1 - pri_weightx[structure_index][x][y][z]) * bp_list[sec_mat_idx[structure_index][x][y][z]] * (Ex[source_index][structure_index][x][y][z][frequency_index] - Ex_1[source_index][structure_index][x][y][z][frequency_index]);
    }
    if (z > 0 && x > 0)
    { // y分量
        Ey[source_index][structure_index][x][y][z][frequency_index] = (Ey[source_index][structure_index][x][y][z][frequency_index] - ((1 + kp_list[pri_mat_idy[structure_index][x][y][z]]) * pri_Jpdty[source_index][structure_index][x][y][z][frequency_index]).real() - ((1 + kp_list[sec_mat_idy[structure_index][x][y][z]]) * sec_Jpdty[source_index][structure_index][x][y][z][frequency_index]).real()) / (epsbeta_y[structure_index][x][y][z] + sigmadt_2y[structure_index][x][y][z]);

        pri_Jpdty[source_index][structure_index][x][y][z][frequency_index] = kp_list[pri_mat_idy[structure_index][x][y][z]] * pri_Jpdty[source_index][structure_index][x][y][z][frequency_index] +
                                                                             pri_weighty[structure_index][x][y][z] * bp_list[pri_mat_idy[structure_index][x][y][z]] * (Ey[source_index][structure_index][x][y][z][frequency_index] - Ey_1[source_index][structure_index][x][y][z][frequency_index]);
        sec_Jpdty[source_index][structure_index][x][y][z][frequency_index] = kp_list[sec_mat_idy[structure_index][x][y][z]] * sec_Jpdty[source_index][structure_index][x][y][z][frequency_index] +
                                                                             (1 - pri_weighty[structure_index][x][y][z]) * bp_list[sec_mat_idy[structure_index][x][y][z]] * (Ey[source_index][structure_index][x][y][z][frequency_index] - Ey_1[source_index][structure_index][x][y][z][frequency_index]);
    }
    if (x > 0 && y > 0)
    { // z分量
        Ez[source_index][structure_index][x][y][z][frequency_index] = (Ez[source_index][structure_index][x][y][z][frequency_index] - ((1 + kp_list[pri_mat_idz[structure_index][x][y][z]]) * pri_Jpdtz[source_index][structure_index][x][y][z][frequency_index]).real() - ((1 + kp_list[sec_mat_idz[structure_index][x][y][z]]) * sec_Jpdtz[source_index][structure_index][x][y][z][frequency_index]).real()) / (epsbeta_z[structure_index][x][y][z] + sigmadt_2z[structure_index][x][y][z]);

        pri_Jpdtz[source_index][structure_index][x][y][z][frequency_index] = kp_list[pri_mat_idz[structure_index][x][y][z]] * pri_Jpdtz[source_index][structure_index][x][y][z][frequency_index] +
                                                                             pri_weightz[structure_index][x][y][z] * bp_list[pri_mat_idz[structure_index][x][y][z]] * (Ez[source_index][structure_index][x][y][z][frequency_index] - Ez_1[source_index][structure_index][x][y][z][frequency_index]);
        sec_Jpdtz[source_index][structure_index][x][y][z][frequency_index] = kp_list[sec_mat_idz[structure_index][x][y][z]] * sec_Jpdtz[source_index][structure_index][x][y][z][frequency_index] +
                                                                             (1 - pri_weightz[structure_index][x][y][z]) * bp_list[sec_mat_idz[structure_index][x][y][z]] * (Ez[source_index][structure_index][x][y][z][frequency_index] - Ez_1[source_index][structure_index][x][y][z][frequency_index]);
    }
}

void Update_E_Dispersion(torch::Tensor Ex, torch::Tensor Ey, torch::Tensor Ez,
                         torch::Tensor Ex_1, torch::Tensor Ey_1, torch::Tensor Ez_1,
                         torch::Tensor pri_weightx, torch::Tensor pri_weighty, torch::Tensor pri_weightz,
                         torch::Tensor pri_mat_idx, torch::Tensor pri_mat_idy, torch::Tensor pri_mat_idz,
                         torch::Tensor sec_mat_idx, torch::Tensor sec_mat_idy, torch::Tensor sec_mat_idz,
                         torch::Tensor epsbeta_x, torch::Tensor epsbeta_y, torch::Tensor epsbeta_z,
                         torch::Tensor sigmadt_2x, torch::Tensor sigmadt_2y, torch::Tensor sigmadt_2z, torch::Tensor kp_list, torch::Tensor bp_list,
                         torch::Tensor pri_Jpdtx, torch::Tensor pri_Jpdty, torch::Tensor pri_Jpdtz, torch::Tensor sec_Jpdtx, torch::Tensor sec_Jpdty, torch::Tensor sec_Jpdtz,
                         torch::Tensor Periodic_num)
{
    // 分配线程和块
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int nx = Ex.size(2);
    const int ny = Ey.size(3);
    const int nz = Ez.size(4);
    const int num_frequencies2 = Ex.size(5);

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies2, 1);

    Update_E_Dispersion_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ex_1.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey_1.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez_1.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        pri_weightx.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_weighty.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_weightz.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_mat_idx.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        pri_mat_idy.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        pri_mat_idz.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_mat_idx.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_mat_idy.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_mat_idz.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        epsbeta_x.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        epsbeta_y.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        epsbeta_z.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2x.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2y.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        sigmadt_2z.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        kp_list.packed_accessor<c10::complex<float>, 1, torch::RestrictPtrTraits, size_t>(),
        bp_list.packed_accessor<c10::complex<float>, 1, torch::RestrictPtrTraits, size_t>(),
        pri_Jpdtx.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        pri_Jpdty.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        pri_Jpdtz.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        sec_Jpdtx.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        sec_Jpdty.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        sec_Jpdtz.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        num_structures, num_frequencies2,
        nx, ny, nz);

    Ex_1.copy_(Ex);
    Ey_1.copy_(Ey);
    Ez_1.copy_(Ez);
}
// 处理周期性
__global__ void E_boundx(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> x_phase_offset, // 包含所有频率的实部和虚部
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> Periodic_num,
    const int num_structures,
    const int num_frequencies, // 总的频率数量
    const int nx, const int ny, const int nz, bool isconj)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t y = linear_index / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 计算源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 计算结构索引
    uint16_t real_index = blockIdx.y % num_frequencies;                         // 计算频率索引
    uint16_t imag_index = real_index + num_frequencies;

    if (y > ny || z > nz || Periodic_num[0] == 0)
        return;

    float real, imag;

    real = x_phase_offset[source_index][real_index];
    if (isconj)
    {
        imag = x_phase_offset[source_index][imag_index]; // 共轭复数的虚部
    }
    else
    {
        imag = -x_phase_offset[source_index][imag_index]; // 非共轭复数的虚部处理
    }
    // 对于Ey的更新，确保共轭和非共轭的虚部正确计算
    if (y < ny)
    {
        Ey[source_index][structure_index][0][y][z][real_index] =
            Ey[source_index][structure_index][nx - 1][y][z][real_index] * real -
            Ey[source_index][structure_index][nx - 1][y][z][imag_index] * imag;

        Ey[source_index][structure_index][0][y][z][imag_index] =
            Ey[source_index][structure_index][nx - 1][y][z][real_index] * imag +
            Ey[source_index][structure_index][nx - 1][y][z][imag_index] * real;

        Ey[source_index][structure_index][nx][y][z][real_index] =
            Ey[source_index][structure_index][1][y][z][real_index] * real +
            Ey[source_index][structure_index][1][y][z][imag_index] * imag;

        Ey[source_index][structure_index][nx][y][z][imag_index] =
            -Ey[source_index][structure_index][1][y][z][real_index] * imag +
            Ey[source_index][structure_index][1][y][z][imag_index] * real;
    }

    // 对于Ez的更新
    if (z < nz)
    {
        Ez[source_index][structure_index][0][y][z][real_index] =
            Ez[source_index][structure_index][nx - 1][y][z][real_index] * real -
            Ez[source_index][structure_index][nx - 1][y][z][imag_index] * imag;

        Ez[source_index][structure_index][0][y][z][imag_index] =
            Ez[source_index][structure_index][nx - 1][y][z][real_index] * imag +
            Ez[source_index][structure_index][nx - 1][y][z][imag_index] * real;

        Ez[source_index][structure_index][nx][y][z][real_index] =
            Ez[source_index][structure_index][1][y][z][real_index] * real +
            Ez[source_index][structure_index][1][y][z][imag_index] * imag;

        Ez[source_index][structure_index][nx][y][z][imag_index] =
            -Ez[source_index][structure_index][1][y][z][real_index] * imag +
            Ez[source_index][structure_index][1][y][z][imag_index] * real;
    }
}
__global__ void E_boundy(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    torch::PackedTensorAccessor<float, 2, torch::RestrictPtrTraits, size_t> y_phase_offset, // 包含所有频率的实部和虚部
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> Periodic_num,
    const int num_structures,
    const int num_frequencies, // 总的频率数量
    const int nx, const int ny, const int nz, bool isconj)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / nz;
    uint16_t z = linear_index % nz;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies);    // 计算源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies) % num_structures; // 计算结构索引
    uint16_t real_index = blockIdx.y % num_frequencies;                         // 计算频率索引
    uint16_t imag_index = real_index + num_frequencies;

    if (x > nx || z > nz || Periodic_num[1] == 0)
        return;

    float real = y_phase_offset[source_index][real_index];
    float imag;
    if (isconj)
    {
        imag = y_phase_offset[source_index][imag_index]; // 共轭复数的虚部
    }
    else
    {
        imag = -y_phase_offset[source_index][imag_index]; // 非共轭复数的虚部处理
    }
    if (x < nx)
    {
        Ex[source_index][structure_index][x][0][z][real_index] =
            Ex[source_index][structure_index][x][ny - 1][z][real_index] * real -
            Ex[source_index][structure_index][x][ny - 1][z][imag_index] * imag;

        Ex[source_index][structure_index][x][0][z][imag_index] =
            Ex[source_index][structure_index][x][ny - 1][z][real_index] * imag +
            Ex[source_index][structure_index][x][ny - 1][z][imag_index] * real;

        Ex[source_index][structure_index][x][ny][z][real_index] =
            Ex[source_index][structure_index][x][1][z][real_index] * real +
            Ex[source_index][structure_index][x][1][z][imag_index] * imag;

        Ex[source_index][structure_index][x][ny][z][imag_index] =
            -Ex[source_index][structure_index][x][1][z][real_index] * imag +
            Ex[source_index][structure_index][x][1][z][imag_index] * real;
    }
    if (z < nz)
    {
        Ez[source_index][structure_index][x][0][z][real_index] =
            Ez[source_index][structure_index][x][ny - 1][z][real_index] * real -
            Ez[source_index][structure_index][x][ny - 1][z][imag_index] * imag;

        Ez[source_index][structure_index][x][0][z][imag_index] =
            Ez[source_index][structure_index][x][ny - 1][z][real_index] * imag +
            Ez[source_index][structure_index][x][ny - 1][z][imag_index] * real;

        Ez[source_index][structure_index][x][ny][z][real_index] =
            Ez[source_index][structure_index][x][1][z][real_index] * real +
            Ez[source_index][structure_index][x][1][z][imag_index] * imag;

        Ez[source_index][structure_index][x][ny][z][imag_index] =
            -Ez[source_index][structure_index][x][1][z][real_index] * imag +
            Ez[source_index][structure_index][x][1][z][imag_index] * real;
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
    const int num_frequencies = Ex.size(5) / 2; // 这里假设 num_frequencies 已经是实部和虚部的总和

    const dim3 threads(256, 1, 1);
    const dim3 blockx((ny * nz + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);
    const dim3 blocky((nx * nz + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    E_boundx<<<blockx, threads>>>(
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        x_phase_offset.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(),
        Periodic_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz, isconj);

    E_boundy<<<blocky, threads>>>(
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        y_phase_offset.packed_accessor<float, 2, torch::RestrictPtrTraits, size_t>(),
        Periodic_num.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx, ny, nz, isconj);
}
// 只需要平面光,启动小的线程即可
// 现在是复数光源.只需要输入当前时刻的光就行了,不管它怎么回事
// 始终牢记,实部和虚部是两套系统
__global__ void Inject_H_Plane_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hx,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Hy,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz2,
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Ext,    //(光源,频率)
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Eyt,    //(光源,频率)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Ex, //(光源,x,y,频率)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Ey, //(光源,x,y,频率)
    const int bound,
    const int PMLx,
    const int PMLy,
    const int num_structures,
    const int num_frequencies2,
    const int nx, const int ny)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / ny;
    uint16_t y = linear_index % ny;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies2);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies2) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t real_index = blockIdx.y % num_frequencies2;                         // 对频率数量取
    if (x >= (nx - PMLx) || y >= (ny - PMLy) || x < PMLx || y < PMLy)
        return;

    if (real_index < (num_frequencies2 / 2))
    {
        if (x > PMLx)
        {
            Hx[source_index][structure_index][x][y][bound][real_index] -= Cz2[bound] * (Eyt[source_index][real_index] * phi_Ey[source_index][x][y][real_index]).real();
        }
        if (y > PMLy)
        {
            Hy[source_index][structure_index][x][y][bound][real_index] += Cz2[bound] * (Ext[source_index][real_index] * phi_Ex[source_index][x][y][real_index]).real();
        }
    }
    else
    {
        uint16_t imag_index = real_index - (num_frequencies2 / 2);
        if (x > PMLx)
        {
            Hx[source_index][structure_index][x][y][bound][real_index] -= Cz2[bound] * (Eyt[source_index][imag_index] * phi_Ey[source_index][x][y][imag_index]).imag();
        }
        if (y > PMLy)
        {
            Hy[source_index][structure_index][x][y][bound][real_index] += Cz2[bound] * (Ext[source_index][imag_index] * phi_Ex[source_index][x][y][imag_index]).imag();
        }
    }
}

void Inject_H(
    // 定义所有的Tensor参数
    torch::Tensor &Hx,
    torch::Tensor &Hy,
    torch::Tensor &Cz2,
    torch::Tensor &Ext,
    torch::Tensor &Eyt,
    torch::Tensor &phi_Ex,
    torch::Tensor &phi_Ey,
    torch::Tensor &PML_num,
    int bound)
{
    // 计算线程和块的维度
    const int num_sources = Hx.size(0);
    const int num_structures = Hx.size(1);
    const int num_frequencies2 = Hx.size(5);
    const int nx = phi_Ex.size(1);
    const int ny = phi_Ey.size(2);
    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny + 256 - 1) / 256, num_structures * num_frequencies2 * num_sources, 1);

    Inject_H_Plane_GPU<<<blocks, threads>>>(
        Hx.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Hy.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Cz2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Ext.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        Eyt.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        phi_Ex.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        phi_Ey.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        bound,
        PML_num[0].item<int>(), // Assuming PML_num is still a Tensor
        PML_num[1].item<int>(),
        num_structures,
        num_frequencies2,
        nx, ny);
}

__global__ void Inject_E_Plane_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> Cz1,
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Hxt,    //(光源,z*3,频率)
    const torch::PackedTensorAccessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t> Hyt,    //(光源,z*3,频率)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Hx, //(光源,x,y,频率)
    const torch::PackedTensorAccessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t> phi_Hy, //(光源,x,y,频率)
    const int bound,
    const int PMLx,
    const int PMLy,
    const int num_structures,
    const int num_frequencies2,
    const int nx, const int ny)
{

    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    uint16_t x = linear_index / ny;
    uint16_t y = linear_index % ny;
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies2);    // 先除以结构和频率的总数得到源索引
    uint16_t structure_index = (blockIdx.y / num_frequencies2) % num_structures; // 先除以频率的数量，然后对结构数量取模得到结构索引
    uint16_t real_index = blockIdx.y % num_frequencies2;                         // 对频率数量取模得到频率索引

    if (x >= (nx - PMLx) || y >= (ny - PMLy) || x < PMLx || y < PMLy)
        return;

    if (real_index < (num_frequencies2 / 2))
    {
        if (y > PMLy)
        {
            Ex[source_index][structure_index][x][y][bound + 1][real_index] +=
                Cz1[bound + 1] * (Hyt[source_index][real_index] * phi_Hy[source_index][x][y][real_index]).real();
        }

        if (x > PMLx)
        {
            Ey[source_index][structure_index][x][y][bound + 1][real_index] -=
                Cz1[bound + 1] * (Hxt[source_index][real_index] * phi_Hx[source_index][x][y][real_index]).real();
        }
    }
    else
    {
        uint16_t imag_index = real_index - (num_frequencies2 / 2);
        if (y > PMLy)
        {
            Ex[source_index][structure_index][x][y][bound + 1][real_index] +=
                Cz1[bound + 1] * (Hyt[source_index][imag_index] * phi_Hy[source_index][x][y][imag_index]).imag();
        }

        if (x > PMLx)
        {
            Ey[source_index][structure_index][x][y][bound + 1][real_index] -=
                Cz1[bound + 1] * (Hxt[source_index][imag_index] * phi_Hx[source_index][x][y][imag_index]).imag();
        }
    }
}

void Inject_E(
    // 定义所有的Tensor参数
    torch::Tensor &Ex,
    torch::Tensor &Ey,
    torch::Tensor &Cz1,
    torch::Tensor &Hxt,
    torch::Tensor &Hyt,
    torch::Tensor &phi_Hx,
    torch::Tensor &phi_Hy,
    torch::Tensor &PML_num,
    int bound)
{
    // 从Tensor尺寸中提取维度信息，确保对于Ex和Ey使用正确的空间维度
    const int num_sources = Ex.size(0);
    const int num_structures = Ex.size(1);
    const int num_frequencies2 = Ex.size(5);
    const int nx = Ex.size(2); // X维度
    const int ny = Ey.size(3); // Y维度，确保使用Ey的尺寸

    // 计算线程和块的维度
    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny + 256 - 1) / 256, num_structures * num_frequencies2 * num_sources, 1);

    Inject_E_Plane_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Cz1.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        Hxt.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        Hyt.packed_accessor<c10::complex<float>, 2, torch::RestrictPtrTraits, size_t>(),
        phi_Hx.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        phi_Hy.packed_accessor<c10::complex<float>, 4, torch::RestrictPtrTraits, size_t>(),
        bound,
        PML_num[0].item<int>(), // Assuming PML_num is still a Tensor
        PML_num[1].item<int>(),
        num_structures,
        num_frequencies2,
        nx, ny);
}

__global__ void Inject_J_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ex,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ey,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> Ez,
    const torch::PackedTensorAccessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t> Jx,
    const torch::PackedTensorAccessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t> Jy,
    const torch::PackedTensorAccessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t> Jz,
    const int nx_offset, const int ny_offset, const int nz_offset,
    const int num_structures,
    const int num_frequencies2,
    const int nx, const int ny, const int nz)
{

    // Derive indices from blockIdx.y
    uint16_t source_index = blockIdx.y / (num_structures * num_frequencies2);
    uint16_t structure_index = (blockIdx.y / num_frequencies2) % num_structures;
    uint16_t frequency_index = blockIdx.y % num_frequencies2;

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
    if (frequency_index < (num_frequencies2 / 2))
    {
        if (x < nx)
        {
            Ex[source_index][structure_index][xD][yD][zD][frequency_index] -= Jx[source_index][structure_index][x][y][z].real();
        }
        if (y < ny)
        {
            Ey[source_index][structure_index][xD][yD][zD][frequency_index] -= Jy[source_index][structure_index][x][y][z].real();
        }
        if (z < nz)
        {
            Ez[source_index][structure_index][xD][yD][zD][frequency_index] -= Jz[source_index][structure_index][x][y][z].real();
        }
    }
    else
    {
        if (x < nx)
        {
            Ex[source_index][structure_index][xD][yD][zD][frequency_index] -= Jx[source_index][structure_index][x][y][z].imag();
        }
        if (y < ny)
        {
            Ey[source_index][structure_index][xD][yD][zD][frequency_index] -= Jy[source_index][structure_index][x][y][z].imag();
        }
        if (z < nz)
        {
            Ez[source_index][structure_index][xD][yD][zD][frequency_index] -= Jz[source_index][structure_index][x][y][z].imag();
        }
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
    const int num_frequencies2 = Ex.size(5);
    const int nx = Jx.size(2);
    const int ny = Jy.size(3);
    const int nz = Jz.size(4);

    const int nx_offset = n_offset[0].item<int>();
    const int ny_offset = n_offset[1].item<int>();
    const int nz_offset = n_offset[2].item<int>();

    const int total = nx * ny * nz;
    const dim3 threads(256, 1, 1);
    const dim3 blocks((total + 256 - 1) / 256, num_sources * num_structures * num_frequencies2, 1);

    Inject_J_GPU<<<blocks, threads>>>(
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Jx.packed_accessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t>(),
        Jy.packed_accessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t>(),
        Jz.packed_accessor<c10::complex<float>, 5, torch::RestrictPtrTraits, size_t>(),
        nx_offset, ny_offset, nz_offset, num_structures, num_frequencies2, nx, ny, nz);
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
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> epsbeta,            // (结构并行,x,y,z)
    const torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weight,   //(p,x,y,z)
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> epsbeta_list, //(材料数目,波长,只支持实数)
    int nx, int ny, int nz)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int i = linear_index / (ny * nz);
    int j = (linear_index % (ny * nz)) / nz;
    int k = linear_index % nz;

    int p = blockIdx.y; // 波长索引

    if (i >= nx || j >= ny || k >= nz)
        return; // Check bounds
    epsbeta[p][i][j][k] = pri_weight[p][i][j][k] * epsbeta_list[pri_id_mat[p][i][j][k]] + (1 - pri_weight[p][i][j][k]) * epsbeta_list[sec_id_mat[p][i][j][k]];
}

void Set_ER_average(torch::Tensor epsbeta, torch::Tensor pri_weight, torch::Tensor pri_id_mat, torch::Tensor sec_id_mat, torch::Tensor epsbeta_list)
{
    int nx, ny, nz;
    nx = epsbeta.size(1);
    ny = epsbeta.size(2);
    nz = epsbeta.size(3);
    int np = epsbeta.size(0); // Parallel dimension size
    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny * nz + 256 - 1) / 256, np, 1);
    Set_ER_average_GPU<<<blocks, threads>>>(
        epsbeta.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_weight.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        epsbeta_list.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        nx, ny, nz);
}

__global__ void Set_weight_subcell_GPU(
    torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> pri_weight, // (结构并行,x,y,z,波长)
    const torch::PackedTensorAccessor<float, 5, torch::RestrictPtrTraits, size_t> N,    // (结构并行,x,y,z,分量)
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y2,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z2,
    const torch::PackedTensorAccessor<float, 4, torch::RestrictPtrTraits, size_t> mat_in, // (结构并行,x,y,z)
    const int pri_id,
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> pri_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<uint8_t, 4, torch::RestrictPtrTraits, size_t> sec_id_mat, //(p,x,y,z)
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> er_mean_re_list,
    const int dim, // 维度
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

    int p = blockIdx.y;

    if (i >= nx || j >= ny || k >= nz)
        return; // Check bounds

    int x_out = i + x_range_start_id;
    int y_out = j + y_range_start_id;
    int z_out = k + z_range_start_id;

    if (pri_id != pri_id_mat[p][x_out][y_out][z_out])
        return;
    if (er_mean_re_list[pri_id_mat[p][x_out][y_out][z_out]] <= 0 || er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]] <= 0)
    {
        pri_weight[p][x_out][y_out][z_out] = round(pri_weight[p][x_out][y_out][z_out]); // 如果有金属参与,则之间阶梯插值.
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

                    F += weight * (mat_in[p][x][y][z] * er_mean_re_list[pri_id] + (1 - mat_in[p][x][y][z]) * er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]]);

                    Reciprocal_average += weight / (mat_in[p][x][y][z] * er_mean_re_list[pri_id] + (1 - mat_in[p][x][y][z]) * er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]]);
                }
            }
        }
    }

    F += (1 - total_weight) * er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]];
    Reciprocal_average += (1 - total_weight) / er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]];

    // 如果两个材料的er都大于0才能用子像素平滑,否则还是用最近邻插值
    if (dim == 0)
    {
        pri_weight[p][x_out][y_out][z_out] = 1 / (N[p][x_out][y_out][z_out][0] * N[p][x_out][y_out][z_out][0] * Reciprocal_average + (1 - N[p][x_out][y_out][z_out][0] * N[p][x_out][y_out][z_out][0]) / F);
    }
    else if (dim == 1)
    {
        pri_weight[p][x_out][y_out][z_out] = 1 / (N[p][x_out][y_out][z_out][1] * N[p][x_out][y_out][z_out][1] * Reciprocal_average + (1 - N[p][x_out][y_out][z_out][1] * N[p][x_out][y_out][z_out][1]) / F);
    }
    else
    {
        pri_weight[p][x_out][y_out][z_out] = 1 / (N[p][x_out][y_out][z_out][2] * N[p][x_out][y_out][z_out][2] * Reciprocal_average + (1 - N[p][x_out][y_out][z_out][2] * N[p][x_out][y_out][z_out][2]) / F);
    }
    pri_weight[p][x_out][y_out][z_out] = abs(pri_weight[p][x_out][y_out][z_out] - er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]]) /
                                         (EPSILONf + max(er_mean_re_list[pri_id_mat[p][x_out][y_out][z_out]], er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]]) - min(er_mean_re_list[pri_id_mat[p][x_out][y_out][z_out]], er_mean_re_list[sec_id_mat[p][x_out][y_out][z_out]]));
}

std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> Set_weight_subcell(const torch::Tensor &x_range, const torch::Tensor &y_range, const torch::Tensor &z_range, const torch::Tensor &mat_in, const torch::Tensor &x2, const torch::Tensor &y2, const torch::Tensor &z2, torch::Tensor epsbeta, int pri_id, torch::Tensor pri_id_mat, torch::Tensor sec_id_mat, torch::Tensor N, const torch::Tensor er_mean_re_list, int dim)
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

    int np = mat_in.size(0); // Parallel dimension size
    nxs = mat_in.size(1);
    nys = mat_in.size(2);
    nzs = mat_in.size(3);
    nx2 = x2.size(0);
    ny2 = y2.size(0);
    nz2 = z2.size(0);

    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx * ny * nz + 256 - 1) / 256, np, 1);
    Set_weight_subcell_GPU<<<blocks, threads>>>(
        epsbeta.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        N.packed_accessor<float, 5, torch::RestrictPtrTraits, size_t>(),
        x2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z2.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        mat_in.packed_accessor<float, 4, torch::RestrictPtrTraits, size_t>(),
        pri_id,
        pri_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        sec_id_mat.packed_accessor<uint8_t, 4, torch::RestrictPtrTraits, size_t>(),
        er_mean_re_list.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        dim,
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
    int source_index = blockIdx.y / (num_structures * num_frequencies);
    int structure_index = (blockIdx.y / num_frequencies) % num_structures;
    int frequency_index = blockIdx.y % num_frequencies;

    if (i >= nxb || j >= nyb || k >= nzb)
        return;

    int x = i + x_range_start_id;
    int y = j + y_range_start_id;
    int z = k + z_range_start_id;

    // 判断输入Ex/Ey/Ez的最后一维是否小于Exw的频率维度
    bool single_frequency_input = Ex.size(5) < Exw.size(5);

    int input_freq_index = single_frequency_input ? 0 : frequency_index;

    if (i < nxb - 1)
    {
        Exw[source_index][structure_index][i][j][k][frequency_index] +=
            kernel[frequency_index] * Ex[source_index][structure_index][x][y][z][input_freq_index];
    }
    if (j < nyb - 1)
    {
        Eyw[source_index][structure_index][i][j][k][frequency_index] +=
            kernel[frequency_index] * Ey[source_index][structure_index][x][y][z][input_freq_index];
    }
    if (k < nzb - 1)
    {
        Ezw[source_index][structure_index][i][j][k][frequency_index] +=
            kernel[frequency_index] * Ez[source_index][structure_index][x][y][z][input_freq_index];
    }
}

void Monitor_Update_E(
    torch::Tensor &Exw, torch::Tensor &Eyw, torch::Tensor &Ezw,
    const torch::Tensor &Ex, const torch::Tensor &Ey, const torch::Tensor &Ez,
    const torch::Tensor &kernel, const torch::Tensor &x_range, const torch::Tensor &y_range, const torch::Tensor &z_range)
{
    const int num_sources = Exw.size(0);
    const int num_structures = Exw.size(1);
    const int num_frequencies = Exw.size(5);
    int nxb = x_range[1].item<int>() - x_range[0].item<int>() + 2;
    int nyb = y_range[1].item<int>() - y_range[0].item<int>() + 2;
    int nzb = z_range[1].item<int>() - z_range[0].item<int>() + 2;

    const dim3 threads(256, 1, 1);
    const dim3 blocks((nxb * nyb * nzb + 256 - 1) / 256, num_sources * num_structures * num_frequencies, 1);

    Monitor_Update_GPU_E<<<blocks, threads>>>(
        Exw.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Eyw.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ezw.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        Ex.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ey.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        Ez.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        kernel.packed_accessor<c10::complex<float>, 1, torch::RestrictPtrTraits, size_t>(),
        x_range[0].item<int>(), y_range[0].item<int>(), z_range[0].item<int>(),
        num_structures,
        num_frequencies,
        nxb, nyb, nzb);
}

__global__ void Trilinear_interpolation_GPU(
    torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> result,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x_i,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y_i,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z_i,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> x_id,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> y_id,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> z_id,
    const torch::PackedTensorAccessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t> data,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z,
    const int num_structures,
    const int num_frequencies,
    int nx_i, int ny_i, int nz_i, bool nearest)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int source_index = blockIdx.y / (num_structures * num_frequencies);    // Calculate the source index
    int structure_index = (blockIdx.y / num_frequencies) % num_structures; // Calculate the structure index
    int frequency_index = blockIdx.y % num_frequencies;                    // Calculate the frequency index

    int i = linear_index / (ny_i * nz_i);
    int j = (linear_index % (ny_i * nz_i)) / nz_i;
    int k = linear_index % nz_i;

    if (i >= nx_i || j >= ny_i || k >= nz_i)
        return; // Check bounds to prevent out of bounds access

    int idx = x_id[i];
    int idy = y_id[j];
    int idz = z_id[k];

    if (nearest)
    {
        result[source_index][structure_index][i][j][k][frequency_index] = data[source_index][structure_index][idx][idy][idz][frequency_index];
    }
    else
    {
        float xd = (x_i[i] - x[idx]) / (x[idx + 1] - x[idx]);
        float yd = (y_i[j] - y[idy]) / (y[idy + 1] - y[idy]);
        float zd = (z_i[k] - z[idz]) / (z[idz + 1] - z[idz]);

        xd = fmaxf(0.0, fminf(xd, 1.0));
        yd = fmaxf(0.0, fminf(yd, 1.0));
        zd = fmaxf(0.0, fminf(zd, 1.0));

        // Perform trilinear interpolation directly in the formula
        result[source_index][structure_index][i][j][k][frequency_index] =
            (1 - xd) * (1 - yd) * (1 - zd) * data[source_index][structure_index][idx][idy][idz][frequency_index] +
            xd * (1 - yd) * (1 - zd) * data[source_index][structure_index][idx + 1][idy][idz][frequency_index] +
            (1 - xd) * yd * (1 - zd) * data[source_index][structure_index][idx][idy + 1][idz][frequency_index] +
            (1 - xd) * (1 - yd) * zd * data[source_index][structure_index][idx][idy][idz + 1][frequency_index] +
            xd * yd * (1 - zd) * data[source_index][structure_index][idx + 1][idy + 1][idz][frequency_index] +
            (1 - xd) * yd * zd * data[source_index][structure_index][idx][idy + 1][idz + 1][frequency_index] +
            xd * (1 - yd) * zd * data[source_index][structure_index][idx + 1][idy][idz + 1][frequency_index] +
            xd * yd * zd * data[source_index][structure_index][idx + 1][idy + 1][idz + 1][frequency_index];
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

torch::Tensor Trilinear_interpolation(const torch::Tensor &x, const torch::Tensor &y, const torch::Tensor &z,
                                      torch::Tensor &mat_in, const torch::Tensor &x_i, const torch::Tensor &y_i,
                                      const torch::Tensor &z_i, bool nearest)
{
    if (!torch::cuda::is_available())
    {
        throw std::runtime_error("CUDA not available.");
    }
    if (mat_in.device().type() != torch::kCUDA || x.device().type() != torch::kCUDA || y.device().type() != torch::kCUDA || z.device().type() != torch::kCUDA || x_i.device().type() != torch::kCUDA || y_i.device().type() != torch::kCUDA || z_i.device().type() != torch::kCUDA)
    {
        throw std::runtime_error("Tensor is not on GPU.");
    }

    int nx_i = x_i.size(0);
    int ny_i = y_i.size(0);
    int nz_i = z_i.size(0);
    int source_num = mat_in.size(0);      // Number of sources
    int num_structures = mat_in.size(1);  // Number of structures
    int num_frequencies = mat_in.size(5); // Corrected frequency dimension index

    // Define the output tensor for the result with explicit dimensions
    auto options = torch::TensorOptions().dtype(mat_in.dtype()).device(torch::kCUDA);
    torch::Tensor result = torch::zeros({source_num, num_structures, nx_i, ny_i, nz_i, num_frequencies}, options);

    // Get ids for interpolation indices
    torch::Tensor x_id = get_id(x_i, x, nearest);
    torch::Tensor y_id = get_id(y_i, y, nearest);
    torch::Tensor z_id = get_id(z_i, z, nearest);

    // Define block and thread dimensions for the kernel
    const dim3 threads(256, 1, 1);
    int total_blocks = (nx_i * ny_i * nz_i + 255) / 256;
    const dim3 blocks(total_blocks, source_num * num_structures * num_frequencies, 1); // Corrected blocks for frequency handling

    // Launch the kernel using ATen
    Trilinear_interpolation_GPU<<<blocks, threads>>>(
        result.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        x_i.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y_i.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z_i.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        x_id.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        y_id.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        z_id.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        mat_in.packed_accessor<c10::complex<float>, 6, torch::RestrictPtrTraits, size_t>(),
        x.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(), num_structures, num_frequencies,
        nx_i, ny_i, nz_i, nearest);
    cudaDeviceSynchronize(); // Ensure CUDA kernel has finished

    return result;
}

__global__ void Trilinear_reverse_interpolation_GPU(
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> re_i,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> im_i,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x_i,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y_i,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z_i,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> x_id,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> y_id,
    const torch::PackedTensorAccessor<int, 1, torch::RestrictPtrTraits, size_t> z_id,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> re,
    torch::PackedTensorAccessor<float, 6, torch::RestrictPtrTraits, size_t> im,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> x,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> y,
    const torch::PackedTensorAccessor<float, 1, torch::RestrictPtrTraits, size_t> z,
    const int num_structures,
    const int num_frequencies,
    int nx_i, int ny_i, int nz_i)
{
    int linear_index = blockIdx.x * blockDim.x + threadIdx.x;
    int source_index = blockIdx.y / (num_structures * num_frequencies);
    int structure_index = (blockIdx.y / num_frequencies) % num_structures;
    int frequency_index = blockIdx.y % num_frequencies;

    int i = linear_index / (ny_i * nz_i);
    int j = (linear_index % (ny_i * nz_i)) / nz_i;
    int k = linear_index % nz_i;

    if (i >= nx_i || j >= ny_i || k >= nz_i)
        return; // Check bounds

    int idx = x_id[i];
    int idy = y_id[j];
    int idz = z_id[k];

    float xd = (x_i[i] - x[idx]) / (x[idx + 1] - x[idx]);
    float yd = (y_i[j] - y[idy]) / (y[idy + 1] - y[idy]);
    float zd = (z_i[k] - z[idz]) / (z[idz + 1] - z[idz]);

    xd = fmaxf(0.0, fminf(xd, 1.0));
    yd = fmaxf(0.0, fminf(yd, 1.0));
    zd = fmaxf(0.0, fminf(zd, 1.0));

    // Calculate volume correction factor
    float volume_correction = 1.0;

    // Use atomic operations to update the Yee grid
    atomicAdd(&re[source_index][structure_index][idx][idy][idz][frequency_index], (1 - xd) * (1 - yd) * (1 - zd) * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx + 1][idy][idz][frequency_index], xd * (1 - yd) * (1 - zd) * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx][idy + 1][idz][frequency_index], (1 - xd) * yd * (1 - zd) * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx][idy][idz + 1][frequency_index], (1 - xd) * (1 - yd) * zd * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx + 1][idy + 1][idz][frequency_index], xd * yd * (1 - zd) * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx][idy + 1][idz + 1][frequency_index], (1 - xd) * yd * zd * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx + 1][idy][idz + 1][frequency_index], xd * (1 - yd) * zd * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&re[source_index][structure_index][idx + 1][idy + 1][idz + 1][frequency_index], xd * yd * zd * re_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);

    atomicAdd(&im[source_index][structure_index][idx][idy][idz][frequency_index], (1 - xd) * (1 - yd) * (1 - zd) * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx + 1][idy][idz][frequency_index], xd * (1 - yd) * (1 - zd) * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx][idy + 1][idz][frequency_index], (1 - xd) * yd * (1 - zd) * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx][idy][idz + 1][frequency_index], (1 - xd) * (1 - yd) * zd * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx + 1][idy + 1][idz][frequency_index], xd * yd * (1 - zd) * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx][idy + 1][idz + 1][frequency_index], (1 - xd) * yd * zd * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx + 1][idy][idz + 1][frequency_index], xd * (1 - yd) * zd * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
    atomicAdd(&im[source_index][structure_index][idx + 1][idy + 1][idz + 1][frequency_index], xd * yd * zd * im_i[source_index][structure_index][i][j][k][frequency_index] * volume_correction);
}

torch::Tensor Trilinear_reverse_interpolation(const torch::Tensor &x, const torch::Tensor &y, const torch::Tensor &z, torch::Tensor &mat_in, const torch::Tensor &x_i, const torch::Tensor &y_i, const torch::Tensor &z_i)
{
    if (!torch::cuda::is_available())
    {
        throw std::runtime_error("CUDA not available.");
    }
    if (mat_in.device().type() != torch::kCUDA || x.device().type() != torch::kCUDA || y.device().type() != torch::kCUDA || z.device().type() != torch::kCUDA || x_i.device().type() != torch::kCUDA || y_i.device().type() != torch::kCUDA || z_i.device().type() != torch::kCUDA)
    {
        throw std::runtime_error("Error: Tensor is not on GPU.");
    }

    int nx_i = x_i.size(0);
    int ny_i = y_i.size(0);
    int nz_i = z_i.size(0);
    int num_sources = mat_in.size(0);
    int num_structures = mat_in.size(1);
    int num_frequencies = mat_in.size(5);

    torch::Tensor re_i = torch::real(mat_in);
    torch::Tensor im_i = torch::imag(mat_in);
    torch::Tensor re = torch::zeros({num_sources, num_structures, x.size(0), y.size(0), z.size(0), num_frequencies}, torch::kCUDA);
    torch::Tensor im = torch::zeros({num_sources, num_structures, x.size(0), y.size(0), z.size(0), num_frequencies}, torch::kCUDA);

    torch::Tensor x_id = get_id(x_i, x);
    torch::Tensor y_id = get_id(y_i, y);
    torch::Tensor z_id = get_id(z_i, z);

    const dim3 threads(256, 1, 1);
    const dim3 blocks((nx_i * ny_i * nz_i + 255) / 256, num_sources * num_structures * num_frequencies, 1);
    Trilinear_reverse_interpolation_GPU<<<blocks, threads>>>(
        re_i.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        im_i.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        x_i.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y_i.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z_i.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        x_id.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        y_id.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        z_id.packed_accessor<int, 1, torch::RestrictPtrTraits, size_t>(),
        re.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        im.packed_accessor<float, 6, torch::RestrictPtrTraits, size_t>(),
        x.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        y.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        z.packed_accessor<float, 1, torch::RestrictPtrTraits, size_t>(),
        num_structures,
        num_frequencies,
        nx_i, ny_i, nz_i);
    cudaDeviceSynchronize(); // Ensure CUDA kernel has finished

    return torch::complex(re, im);
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
    m.def("Update_E_Dispersion", &Update_E_Dispersion, "Update_E_Dispersion");
    m.def("Update_H", &Update_H, "Update_H");
    m.def("Update_E", &Update_E, "Update_E");
    m.def("Update_E_Periodic", &Update_E_Periodic, "Update_E_Periodic");
    m.def("Inject_H", &Inject_H, "Inject_H");
    m.def("Inject_E", &Inject_E, "Inject_E");
    m.def("Inject_J", &Inject_J, "Inject_J");
    m.def("get_id_range", &get_id_range, "get_id_range");
    m.def("Mat_average", &Mat_average, "Average sampling for index");
    m.def("Set_weight_mat_id", &Set_weight_mat_id, "Set_weight_mat_id");
    m.def("Set_ER_average", &Set_ER_average, "Set_ER_average");
    m.def("Set_weight_subcell", &Set_weight_subcell, "Set_weight_subcell");
    m.def("Monitor_Update_E", &Monitor_Update_E, "Monitor_Update_E");
    m.def("Trilinear_interpolation", &Trilinear_interpolation, "Trilinear_interpolation");
    m.def("Trilinear_reverse_interpolation", &Trilinear_reverse_interpolation, "Trilinear_reverse_interpolation");
}
