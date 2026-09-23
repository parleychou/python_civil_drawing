"""以不同颜色和标签分类渲染 Mesh 各要素。

提取网格顶点和面片进行差异化着色（顶点用海绿色 seagreen，面片用麦黄色 wheat），
并添加顶点标记，使学生能够理解网格表达的视觉组成。
"""

import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


import sys
from pathlib import Path

# 动态寻找第 04 章的脚本目录，以便导入公共的 RenderEngine
def find_chapter_scripts(prefix: str) -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        try:
            for child in parent.iterdir():
                if child.is_dir() and child.name.startswith(prefix):
                    scripts_sub = child / "scripts"
                    return scripts_sub if scripts_sub.exists() else child
        except OSError:
            continue
    return Path()

scripts_dir = Path(__file__).resolve().parent
ch4_path = find_chapter_scripts("04")
sys.path.insert(0, str(scripts_dir))
if ch4_path.exists():
    sys.path.insert(0, str(ch4_path))

from brep_primitives import create_pyramid_mesh
from render_engine import RenderEngine


def main() -> None:
    # 1. 实例化四棱锥 Mesh 对象
    pyramid = create_pyramid_mesh(2000.0, 2000.0, 2000.0)

    # 2. 初始化渲染引擎
    engine = RenderEngine(window_size=(1024, 768), show_grid=True)

    # 3. 渲染多边形面片 (Faces) —— 麦黄色
    engine.add_mesh(
        pyramid.to_pyvista(),
        color="wheat",
        show_edges=True,  # 显示网格边缘细线，方便看清拼合结构
        opacity=1.0
    )

    # 4. 渲染网格顶点并贴上标签 (Vertices) —— 海绿色点与 MV0-MV4 标签
    for idx, v in enumerate(pyramid.vertices):
        engine.render_point(
            v.to_tuple(),
            color="seagreen",
            point_size=15.0,
            label=f"MV{idx}"
        )

    # 5. 显示窗口并提示控制指令
    print(f"[*] 正在渲染 Mesh 四棱锥...")
    print(f"    - 网格面片：麦黄色 (wheat) + 边缘网格线")
    print(f"    - 网格顶点：海绿色圆点 (seagreen) + 顶点标签")
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()
