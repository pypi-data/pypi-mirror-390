"""
PyPI 上传凭证配置
⚠️ 警告：此文件包含敏感信息，请勿提交到 Git！

使用方法：
1. 在此文件中填入你的 PyPI 凭证
2. 确保此文件在 .gitignore 中（已自动配置）
3. 脚本会自动读取此文件中的凭证
"""

# PyPI 正式环境凭证
PYPI_USERNAME = "__token__"  # 使用 API token 时通常是 "__token__"
PYPI_PASSWORD = "pypi-AgEIcHlwaS5vcmcCJDYxM2I1NjRhLTM5NmItNGEzMC1hOGJhLTVkODk1MDhhMWUxZgACKlszLCI0NDhmZjJhNC1kZjZiLTQ3YzUtOTJkNy02M2RhOTBjNGE3NDkiXQAABiCXOANvJOGccx-1o6XBriqJaALbu7yip42-Rl5HW3zNVQ"

# Test PyPI 凭证（可选，如果未设置会使用上面的凭证）
TEST_PYPI_USERNAME = "__token__"
TEST_PYPI_PASSWORD = ""  # 填入你的 Test PyPI API token

