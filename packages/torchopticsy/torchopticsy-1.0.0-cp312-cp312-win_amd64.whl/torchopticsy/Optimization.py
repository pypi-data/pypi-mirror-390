# %%放置一些优化相关的常用函数
# 包括随机扰动的鲁棒性直方图分析
# 现在需要考虑一个维度为1的情况了

import torch
from torch import tensor, zeros, norm
from torchopticsy.FDTD.Structure import create_distance_weighted_kernel
import numpy as np
import torchopticsy.mma as mma
from torchvision.transforms.functional import gaussian_blur
import torch.nn.functional as F


def Sensitivity_filtering(input_tensor, kernel, periodic_num):
    # 之前没有试过直接对灵敏度滤波,今天试一试
    # 确保输入张量是四维的 (p, x, y, z)
    if input_tensor.dim() != 4:
        raise ValueError("输入张量必须是四维的 (p, x, y, z)")

    # 将核调整为符合卷积操作的形状 (out_channels, in_channels, d, h, w)
    kernel = kernel.unsqueeze(0).unsqueeze(0)

    # 将输入张量调整为符合卷积操作的形状 (batch_size, channels, d, h, w)
    input_tensor = input_tensor.unsqueeze(1)

    # 确定填充大小
    padding = kernel.size(2) // 2  # 多出一格用于卷积

    # 根据 periodic_num 设置填充模式

    # 逐个维度应用填充
    if periodic_num[0] > 0:
        input_tensor = F.pad(
            input_tensor, (0, 0, 0, 0, padding, padding), mode="circular"
        )
    else:
        input_tensor = F.pad(
            input_tensor, (0, 0, 0, 0, padding, padding), mode="reflect"
        )
    if periodic_num[1] > 0:
        input_tensor = F.pad(
            input_tensor, (0, 0, padding, padding, 0, 0), mode="circular"
        )
    else:
        input_tensor = F.pad(
            input_tensor, (0, 0, padding, padding, 0, 0), mode="reflect"
        )

    if periodic_num[2] > 0:
        input_tensor = F.pad(
            input_tensor, (padding, padding, 0, 0, 0, 0), mode="circular"
        )
    else:
        input_tensor = F.pad(
            input_tensor, (padding, padding, 0, 0, 0, 0), mode="reflect"
        )

    # 应用卷积操作
    input_tensor = F.conv3d(input_tensor, kernel)

    # 调整输出张量的形状回到 (p, x, y, z)
    input_tensor = input_tensor.squeeze(1)
    return input_tensor


# 现在期望Convert_variables直接就能得到完整的结构,包括了滤波二值化等操作
def Convert_variables(variables, show):
    return (
        variables  # 尽管我们可以预先对于场先做变换(累加等)减少计算图中的变量以提高速度
    )
    # 但是从通用性的角度来说,还是直接构造从优化变量到四维矢量的映射最好,并且始终保持材料网格的密度和仿真网格相当.


def FOM(E, x):
    return 0, 0


# 应用位移场到图像
def generate_displacement_fields(size, alpha, sigma, num_fields=4, device="cuda"):
    # 使用矢量化方式生成4个随机位移场
    displacement_x = torch.rand(num_fields, 1, size[0], size[1], device=device) * 2 - 1
    displacement_y = torch.rand(num_fields, 1, size[0], size[1], device=device) * 2 - 1

    # 使用高斯模糊平滑位移场
    displacement_x = gaussian_blur(
        displacement_x, kernel_size=(sigma * 6 + 1, sigma * 6 + 1), sigma=sigma
    )
    displacement_y = gaussian_blur(
        displacement_y, kernel_size=(sigma * 6 + 1, sigma * 6 + 1), sigma=sigma
    )

    # 合并位移场
    displacement_fields = torch.cat((displacement_x, displacement_y), dim=1)

    # 计算平均位移距离
    avg_distance = torch.mean(
        torch.sqrt(
            displacement_fields[:, 0, :, :] ** 2 + displacement_fields[:, 1, :, :] ** 2
        )
    )

    displacement_fields = displacement_fields / (avg_distance + 1e-8)  # 防止除以0

    # 应用缩放因子α
    displacement_fields = displacement_fields * alpha

    return displacement_fields


def apply_displacement(image, displacement_fields):
    # image(x,y)
    # displacement_fields(并行,x,y)
    num_fields = displacement_fields.size(0)
    xsize = image.size(0)
    ysize = image.size(1)

    # 创建网格并扩展到每个位移场
    grid = (
        torch.stack(
            torch.meshgrid(torch.arange(xsize), torch.arange(ysize), indexing="ij"),
            dim=-1,
        )
        .float()
        .to(image.device)
    )
    print(grid.shape)
    grid = grid.unsqueeze(0).expand(
        num_fields, -1, -1, -1
    )  # 扩展为 (num_fields, H, W, 2)

    # 应用位移场到网格
    grid = grid + displacement_fields.permute(0, 2, 3, 1)

    # 归一化坐标
    grid[..., 0] = 2.0 * grid[..., 0] / (xsize - 1) - 1.0
    grid[..., 1] = 2.0 * grid[..., 1] / (ysize - 1) - 1.0

    # 扩展图像维度以匹配批量大小，并应用 grid_sample 进行变换
    image_batch = image.unsqueeze(0).unsqueeze(0).expand(num_fields, -1, -1, -1)
    print(image_batch.shape)
    print(grid.shape)
    transformed_images = F.grid_sample(
        image_batch.permute(0, 1, 3, 2),
        grid.permute(0, 2, 1, 3),
        mode="bilinear",
        align_corners=True,
        padding_mode="border",
    ).permute(0, 1, 3, 2)

    return transformed_images.squeeze(1)  # 返回 (num_fields, H, W)


def generate_uniform_kernel(dx, dy, feature_size, device="cpu"):
    xsize = int(np.ceil(feature_size / dx)) + 1
    if xsize % 2 == 0:
        xsize += 1

    ysize = int(np.ceil(feature_size / dy)) + 1
    if ysize % 2 == 0:
        ysize += 1
    kernel = torch.zeros((xsize, ysize), device=device)

    x = (torch.arange(xsize) - (xsize - 1) / 2) * dx
    y = (torch.arange(ysize) - (ysize - 1) / 2) * dy
    x = x.view(-1, 1)
    y = y.view(1, -1)
    dis = torch.sqrt(x**2 + y**2)
    kernel[dis < feature_size / 2] = 1
    return kernel


# # 有点问题四角怎么也有tm的元素呢?
def generate_linear_kernel(xsize, ysize, device):
    print("滤波直径", [xsize, ysize])
    center = [
        (xsize - 1) / 2,
        (ysize - 1) / 2,
    ]  # Integer division to get the center of the kernel
    kernel = zeros((xsize, ysize), device=device)

    max_distance = norm(tensor(center))

    # Populate the kernel with linearly decaying weights
    for i in range(xsize):
        for j in range(ysize):
            # Compute Euclidean distance to the center
            distance = norm(tensor([i - center[0], j - center[1]]))

            if distance <= max_distance:
                weight = max(0, max_distance - distance)
            else:
                weight = 0  # Outside the range of linear decay
            kernel[i, j] = weight
    kernel /= kernel.sum()
    return kernel


def generate_ellipse_kernel(dx, dy, a, b, device="cpu"):
    xsize = int(np.ceil(a / dx))
    if xsize % 2 == 0:
        xsize += 1

    ysize = int(np.ceil(b / dy))
    if ysize % 2 == 0:
        ysize += 1

    kernel = torch.zeros((xsize, ysize), device=device)

    x = (torch.arange(xsize) - (xsize - 1) / 2) * dx
    y = (torch.arange(ysize) - (ysize - 1) / 2) * dy
    x = x.view(-1, 1)
    y = y.view(1, -1)

    # Calculate the elliptical distance
    dis = torch.sqrt((x / a) ** 2 + (y / b) ** 2)

    kernel[dis < 0.5] = 1  # Set values inside the ellipse to 1
    return kernel


def generate_gaussian_kernel(dx, dy, a, b, device="cpu"):
    xsize = 4 * int(np.ceil(a / dx / 2)) + 1
    ysize = 4 * int(np.ceil(b / dy / 2)) + 1

    # Create grid of coordinates
    x = (torch.arange(xsize, device=device) - (xsize - 1) / 2) * dx
    y = (torch.arange(ysize, device=device) - (ysize - 1) / 2) * dy
    x = x.view(-1, 1)
    y = y.view(1, -1)

    # Calculate the Gaussian function
    exponent = -4 * np.log(2) * ((x**2) / (a**2) + (y**2) / (b**2))
    kernel = torch.exp(exponent)

    # Normalize the kernel so that its sum equals 1
    kernel /= kernel.sum()

    return kernel


def generate_gaussian1D_kernel(dx, a, device="cpu"):
    xsize = 4 * int(np.ceil(a / dx / 2)) + 1

    # Create grid of coordinates
    x = (torch.arange(xsize, device=device) - (xsize - 1) / 2) * dx
    x = x.view(-1, 1)

    # Calculate the Gaussian function
    exponent = -4 * np.log(2) * ((x**2) / (a**2))
    kernel = torch.exp(exponent)

    # Normalize the kernel so that its sum equals 1
    kernel /= kernel.sum()

    return kernel


def sigmoid(y, beta=10.0, eta=0.5):
    beta = tensor(beta).to(y.device)
    z = (torch.tanh(beta * eta) + torch.tanh(beta * (y - eta))) / (
        torch.tanh(beta * eta) + torch.tanh(beta * (1 - eta))
    )
    return z


def filter(x, kernel, mode1="reflect", mode2="reflect"):
    # 只负责卷积模糊
    padding = (kernel.shape[0] // 2, kernel.shape[1] // 2)  # 计算填充的数量
    x_padded = torch.clamp(x, 0, 1)

    x_padded = torch.nn.functional.pad(
        x_padded,
        (0, 0, padding[0], padding[0]),
        mode=mode1,
    )

    x_padded = torch.nn.functional.pad(
        x_padded,
        (padding[1], padding[1], 0, 0),
        mode=mode2,
    )
    y = torch.nn.functional.conv2d(
        x_padded.unsqueeze(1), kernel[None, None, :, :], padding=0
    ).squeeze(
        1
    )  # 注意维度对齐
    return y


class Optimizer:
    # FOM是关于E(x)和x的函数
    def __init__(self, fdtd, structure, opt_Monitor):
        self.debug = fdtd.debug
        self.fdtd = fdtd
        self.structure = structure
        self.Eexc = fdtd.AddMonitor(structure.area, name="Eexc", type="interp")
        self.opt_Monitor = opt_Monitor
        self.LOSSes = []
        self.kernel = (
            create_distance_weighted_kernel(5).to(fdtd.device).to(torch.cfloat)
        )

    def f0df0fdf(self, x):
        torch.cuda.empty_cache()
        Convert_variables = self.Convert_variables
        structure = self.structure
        fdtd = self.fdtd
        FOM = self.FOM
        eps_delta = self.eps_delta
        w = self.w

        projected_mat0 = Convert_variables(x, True)
        structure.Adjust(projected_mat0)  # 调整结构
        fdtd.Update()
        EF = self.Eexc.E.clone()
        self.opt_Monitor.AdjustAdjointSource(FOM, x)

        # 下面才需要x的梯度
        x.requires_grad = True
        FOM0, _ = FOM(self.opt_Monitor.E.detach(), x)

        fdtd.Update(True)
        dot = torch.sum(
            EF * self.Eexc.E * self.Eexc.dV(), dim=(0, 5)
        )  # 对多个光源和分量求和,得到(结构,x,y,z,lam)

        dot = torch.sum(
            dot
            * (
                eps_delta
                + 1j
                * self.structure.sigma
                / w
                * (-2 * projected_mat0[:, :, :, :, None] + 1)
            ),
            dim=-1,
        )  # (并行,x,y,z)

        dot = Sensitivity_filtering(dot, self.kernel, fdtd.periodic_num)  # 灵敏度滤波

        projected_mat = Convert_variables(x, False)
        dFOM_AVM_interp = torch.sum((projected_mat - projected_mat0) * dot)
        dFOM_AVM = torch.real(dFOM_AVM_interp)

        LOSS = dFOM_AVM + FOM0  # 前面是含E的偏导
        try:
            LOSS.backward()  # retain_graph=True
        except Exception as e:
            print(f"Error occurred: {e}")
            print(f"x.requires_grad: {x.requires_grad}")

        f0dx = x.grad.clone()
        x.grad.zero_()

        constraint1 = 0 * torch.mean(x) - 1  #
        try:
            constraint1.backward()  # retain_graph=True
        except Exception as e:
            print(f"Error occurred: {e}")
            print(f"x.requires_grad: {x.requires_grad}")
        f1dx = x.grad.clone()
        x.grad.zero_()

        x.requires_grad = False
        self.LOSSes.append(LOSS.detach())
        return (
            LOSS.detach(),
            f0dx.detach(),
            constraint1.detach().view(-1),
            f1dx.detach().view(1, -1),
        )

    def Run(
        self,
        init_variables,
        variables_min,
        variables_max,
        Convert_variables=Convert_variables,
        FOM=FOM,
        move=0.25,
        num_epochs=25,
    ):
        device = self.fdtd.device
        self.Convert_variables = Convert_variables
        self.FOM = FOM

        init_variables = init_variables.to(device)

        projected_mat = Convert_variables(init_variables, False)
        projected_mat_origin = projected_mat.detach().clone().cpu()
        self.structure.Adjust(projected_mat.detach())  # 调整结构
        self.Eexc.override_grid(self.structure)  # 对齐监视器网格

        self.fdtd.Update()
        self.opt_Monitor.AdjustAdjointSource(FOM, init_variables.detach())
        self.eps_delta = (self.structure.er_pri - self.structure.er_sec).view(
            1, 1, 1, 1, -1
        )  # 能够简化为2维的时代一去不复返啦
        self.w = 2 * torch.pi * self.fdtd.f.reshape(1, 1, 1, 1, -1)

        f, x = mma.Single_Optimizer(
            self.f0df0fdf,
            init_variables.clone(),
            variables_min,
            variables_max,
            maxoutit=num_epochs,
            move=move,
        )
        return x
