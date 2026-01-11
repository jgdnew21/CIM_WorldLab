"""
__main__.py
===========
让你可以直接运行：

  python -m cim_worldlab <command> [options]

例如：
  python -m cim_worldlab run-once
  python -m cim_worldlab replay
  python -m cim_worldlab serve

这就是“项目级 CLI”的最标准入口形式。
"""

from cim_worldlab.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
