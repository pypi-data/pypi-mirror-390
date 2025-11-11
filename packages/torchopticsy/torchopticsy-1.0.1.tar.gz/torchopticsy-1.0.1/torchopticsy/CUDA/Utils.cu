// 累加器在线程中定义时必须置零!!!否则被缓存了结果就G了
// 使用pinv记得根据float设置容差为1e-7否则结果不准.
#include <torch/extension.h>
#include <torch/torch.h>
#include <vector>
#include <cmath>
// 常量定义
#define PI 3.14159265358979323846f

std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> Rational_fitting(const torch::Tensor &w, const torch::Tensor &fw, int poles, int iteration)
{
    // 设置精度
    // CPU版本
    // 生成有理拟合
    // 并行分量统一放在第一维度
    // 先不管内存消耗,后续根据w分块进行处理
    // w是一维实数矩阵
    // fw是一/二维复数矩阵,第二个维度和频率对应,
    // poles是极子数
    // iteration是极子的迭代次数.
    // 返回cp,d,ap,cp和ap_new是二维复数矩阵,d是一维实数矩阵.
    // 创建虚数单位 j，确保在 GPU 上
    // 获取w的设备信息
    const float EPS = 1e-7;
    torch::Tensor j = torch::tensor({c10::complex<float>(0.0, 1.0)}, torch::TensorOptions().dtype(torch::kComplexFloat));
    auto w_expanded = w.unsqueeze(-1); //(w,1)
    float w_max = torch::max(w).item<float>();

    torch::Tensor f_expanded;
    if (fw.dim() == 1)
    {
        f_expanded = fw.unsqueeze(0).unsqueeze(-1);
    }
    else
    {
        f_expanded = fw.unsqueeze(-1);
    }
    int parallel_num = f_expanded.size(0);

    torch::Tensor beta = torch::linspace(torch::min(w).item<float>(), w_max, poles);
    torch::Tensor ap = (-beta / 100 + beta * j).unsqueeze(0);
    ap = ap.repeat({parallel_num, 1}); // ap始终是(并行,极子数)

    torch::Tensor cp = torch::zeros({parallel_num, poles}, torch::dtype(torch::kComplexFloat));
    torch::Tensor d = torch::zeros({parallel_num}, torch::dtype(torch::kFloat32));
    int center = 2 * poles;
    torch::Tensor b = torch::cat({2 * torch::ones({poles, 1}), torch::zeros({poles, 1})}, 0);
    for (int p = 0; p < parallel_num; ++p)
    {
        torch::Tensor f = torch::cat({torch::real(f_expanded[p]), torch::imag(f_expanded[p])}, 0); //(2w,n)
        for (int i = 0; i < iteration; ++i)
        {
            // 先找到cp_
            torch::Tensor A = w_max / (-j * w_expanded - ap[p].unsqueeze(0)) + w_max / (-j * w_expanded - torch::conj(ap[p].unsqueeze(0)));
            torch::Tensor B = w_max / (-j * w_expanded - ap[p].unsqueeze(0)) - w_max / (-j * w_expanded - torch::conj(ap[p].unsqueeze(0)));

            torch::Tensor C = torch::cat({torch::cat({torch::real(A), -torch::imag(B), torch::ones({A.size(0), 1}), torch::real(-f_expanded[p] * A), -torch::imag(-f_expanded[p] * B)}, 1),
                                          torch::cat({torch::imag(A), torch::real(B), torch::zeros({A.size(0), 1}), torch::imag(-f_expanded[p] * A), torch::real(-f_expanded[p] * B)}, 1)},
                                         0);

            torch::Tensor x = torch::sum(torch::linalg::pinv(C, EPS) * f.transpose(0, 1), 1);

            torch::Tensor cp_ = (x.slice(0, center + 1, center + poles + 1) +
                                 x.slice(0, center + poles + 1) * j) *
                                w_max;

            // 然后计算新的极子位置
            C = torch::cat({torch::cat({torch::diag(torch::real(ap[p])), torch::diag(torch::imag(ap[p]))}, 1),
                            torch::cat({-torch::diag(torch::imag(ap[p])), torch::diag(torch::real(ap[p]))}, 1)},
                           0);

            torch::Tensor cT = torch::cat({torch::real(cp_), torch::imag(cp_)}, 0).unsqueeze(0);

            torch::Tensor ap_new = torch::linalg::eigvals(C - b * cT);

            // 步骤1: 选择所有虚部非负的复数
            ap_new = ap_new.index_select(0, torch::nonzero(torch::imag(ap_new) >= 0).squeeze());
            // 步骤2: 如果极点数量仍然大于原始数量，优先剔除实部较大的
            if (ap_new.size(0) > poles)
            {
                torch::Tensor values, indices;
                std::tie(values, indices) = torch::sort(torch::real(ap_new), 0, false); // 实部降序排序
                ap_new = ap_new.index_select(0, indices.slice(0, 0, poles));            // 保留实部较小的极点
            }
            // 步骤3: 将所有实部大于0的极点的实部取负
            ap[p] = torch::where(torch::real(ap_new) > 0, -torch::real(ap_new) + torch::imag(ap_new) * j, ap_new);
        }
        torch::Tensor A = w_max / (-j * w_expanded - ap[p].unsqueeze(0)) + w_max / (-j * w_expanded - torch::conj(ap[p].unsqueeze(0)));
        torch::Tensor B = w_max / (-j * w_expanded - ap[p].unsqueeze(0)) - w_max / (-j * w_expanded - torch::conj(ap[p].unsqueeze(0)));
        torch::Tensor C = torch::cat({torch::cat({torch::real(A), -torch::imag(B), torch::ones({A.size(0), 1})}, 1),
                                      torch::cat({torch::imag(A), torch::real(B), torch::zeros({A.size(0), 1})}, 1)},
                                     0);

        torch::Tensor x = torch::sum(torch::linalg::pinv(C, EPS) * f.transpose(0, 1), 1); //(平行,极子)

        cp[p] = (x.slice(0, 0, poles) + x.slice(0, poles, -1) * j) * w_max;
        d[p] = x[-1];
    }
    return std::make_tuple(cp, d, ap);
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
    m.def("Rational_fitting", &Rational_fitting,
          py::arg("w"),
          py::arg("fw"),
          py::arg("ap"),
          py::arg("iteration"), "Rational fitting for w");
}
