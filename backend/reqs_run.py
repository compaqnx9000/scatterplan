import os

def read_file_universal(file_path):
    """尝试用多种编码读取文件"""
    encodings = ['utf-16', 'utf-8-sig', 'utf-8', 'gbk']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
                print(f"成功使用 {enc} 编码读取 {file_path}")
                return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise Exception(f"无法读取文件 {file_path}，请检查文件格式。")

# 1. 获取 pipreqs 识别到的库名单
try:
    content = read_file_universal('requirements.txt')
    needed = {line.split('==')[0].strip().lower().replace('_', '-') 
              for line in content.splitlines() if line.strip()}
except Exception as e:
    print(e)
    exit()

# 2. 获取你当前环境真实的安装版本
print("正在从当前虚拟环境导出安装列表 (pip freeze)...")
os.system('pip freeze > current_env.txt')

# 3. 读取并匹配版本
current_env_content = read_file_universal('current_env.txt')
final_list = []

for line in current_env_content.splitlines():
    if '==' in line:
        # 处理类似 Django==4.2.1 的行
        package_full_name = line.split('==')[0].strip()
        # 统一转成小写并将下划线转横杠，方便匹配
        package_compare_name = package_full_name.lower().replace('_', '-')
        if package_compare_name in needed:
            final_list.append(line.strip())

# 4. 强制补漏 (有些库 pipreqs 扫不出来但必不可少)
essential_packages = ['whitenoise', 'django-filter', 'gunicorn']
for pkg in essential_packages:
    # 如果当前环境里有这些包，但 final_list 里没有，就补进去
    for line in current_env_content.splitlines():
        if line.lower().startswith(pkg) and '==' in line:
            if line.strip() not in final_list:
                final_list.append(line.strip())

# 5. 写入最终文件
with open('requirements_fixed.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sorted(set(final_list))))

print("\n--- 任务完成 ---")
print(f"已生成的精简名单: requirements_fixed.txt")
print(f"库数量从全环境精简到了: {len(final_list)} 个")