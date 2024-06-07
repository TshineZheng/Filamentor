![](doc/image1.jpg)
# 介绍
Filamentor = Filament + mentor，这是一个3D打印机进退料管理系统（多色打印）。

# 功能
### 已完成
- 打印机对接
    - 拓竹（已验证 a1 mini）
- 基本换料逻辑
    - 送料
        - 主动
        - 被动
    - 退料
- 断料检测
- 可视化配置

### 待完成

- 自发现
- 待补充

# 已适配硬件
- [YBA-AMS-PY](https://github.com/TshineZheng/YBA-AMS-ESP-PY) (修复四通道问题 以及 优化掉线)
- [YBA-AMS](https://makerworld.com/zh/models/396276)

# 使用
双击 `start.bat` 即可。

如果需要配置，访问启动时提示的链接。

# 背景
灵感来源于 [YBA-AMS-Python](https://github.com/YBA0312/YBA-AMS-Python) 项目，在接触和交流过程中，发现有能力修改优化的用户都在重头开始设计硬件，并将逻辑和硬件强制绑定，纵使有其合理合情的原因，但仍然使得已经被制作出来的硬件很可能被淘汰，这将造成浪费，而我认为换料在宏观角度看，无非是：暂停、退料、送料、继续。所以何不尝试独立出这部分，让硬件更加独立专注的优化迭代。

再有，长远来看，仅仅是换料是完全不足以满足需求的，还不如买现成的AMS系统更省事，比如材料/设备的管理、自发现、同步、配置、切片软件交互等等有太多需要待深入的功能，依托于某个绑定硬件来完成会造成极大的研发浪费。（如果每个都做这些的话）

我接触3D打印并不久，以上都是我目前认知下的理解，如有不对，欢迎交流。

纵使 AMS 价格并不贵也稳定，但自制换料系统依然有很大的开发空间，所以我创建了这个项目。

# 愿景
1. 完善的换料逻辑
2. 完善的纠错机制
3. 设备管理（自发现、配置、可拓展等）
4. 可视化
5. 切片软件同步
6. 配置同步
7. 其它打印机适配
8. 可运行在微型设备上
9. more……

这个项目还刚开始，还有更多有意思并值得探索的部分，如果你也感兴趣不如现在就加入进来，如果你觉得没兴趣，也不妨先加入，没准有什么有趣的事情从你身上发生。

# 开发
项目使用 Python，是因为它更加亲民、更加方便移植、易开发等，生态也足够。用它来制作是完全足以应付的。作为一个平常不怎么使用python的普通人，都可以在gpt的帮助下完成代码编写，也是希望能有更多的人能参与进来。

# 问答
Q：为什么不在 YBA-AMS-Python 基础上研发？  
A：尝试过了，也提交了pr，但原项目确实有点太早期了，无法确定和其项目能保持目标一至。

Q：我该用什么硬件配合使用？  
A：这个项目不包含硬件设计，仅作为软件系统设计，你可以比作为这是一个打印机版的homeassistant（有点夸张），你需要自己增加你的硬件。
