import requests
import json

def test_ollama_connection(base_url="http://localhost:11434"):
    """
    测试 Ollama 服务是否正常工作
    
    参数:
        base_url: Ollama API 基础地址，默认是 http://localhost:11434
    
    返回:
        bool: 连接是否成功
    """
    try:
        # 1. 测试 API 基础连通性
        print(f"正在测试连接: {base_url}")
        
        # 尝试获取可用模型列表（最直接的测试方法）
        response = requests.get(f"{base_url}/api/tags")
        
        if response.status_code == 200:
            models = response.json()
            model_list = models.get('models', [])
            
            print("✅ 连接成功！")
            print(f"Ollama 版本: {models.get('ollama_version', '未知')}")
            
            if model_list:
                print("已下载的模型:")
                for model in model_list:
                    print(f"  - {model.get('name')} (大小: {model.get('size', 0) // 10**9}GB)")
            else:
                print("⚠️  未找到已下载的模型，使用 /api/pull 拉取一个模型")
            
            return True
        else:
            print(f"❌ 连接失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 {base_url}")
        print("请检查:")
        print("  1. Ollama 是否已启动（终端输入 'ollama serve'）")
        print("  2. 端口 11434 是否正确")
        print("  3. 防火墙是否阻止了连接")
        return False
    except Exception as e:
        print(f"❌ 发生未知错误: {type(e).__name__}: {e}")
        return False

def test_chat_model(base_url="http://localhost:11434", model="llama2"):
    """
    测试与模型的聊天功能是否正常
    
    参数:
        base_url: Ollama API 基础地址
        model: 要测试的模型名称，默认 llama2
    """
    print(f"\n正在测试模型 '{model}' 的聊天功能...")
    
    # 准备聊天请求数据
    chat_data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "你好！请简单介绍一下你自己。用一句话回答即可。"
            }
        ],
        "stream": False  # 设置为 True 可以流式接收响应
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'message' in result and 'content' in result['message']:
                print("✅ 聊天功能正常！")
                print(f"模型回复: {result['message']['content']}")
                return True
            else:
                print("❌ 响应格式异常:", result)
                return False
        elif response.status_code == 404:
            print(f"❌ 模型 '{model}' 不存在")
            print("请先下载模型:")
            print(f"  终端执行: ollama pull {model}")
            return False
        else:
            print(f"❌ 聊天请求失败，状态码: {response.status_code}")
            print("响应内容:", response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ 聊天测试失败: {type(e).__name__}: {e}")
        return False

def test_generate_model(base_url="http://localhost:11434", model="llama2"):
    """
    测试模型的生成功能（简化版聊天，用于兼容性测试）
    """
    print(f"\n正在测试模型 '{model}' 的生成功能...")
    
    generate_data = {
        "model": model,
        "prompt": "用一句话说'你好，世界！'",
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=generate_data,
            timeout=30  # 设置超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 生成功能正常！")
            print(f"模型回复: {result.get('response', '无内容')}")
            return True
        else:
            print(f"❌ 生成请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，模型可能需要更长时间响应")
        return False
    except Exception as e:
        print(f"❌ 生成测试失败: {e}")
        return False

def test_health_status(base_url="http://localhost:11434"):
    """
    测试 Ollama 健康状态
    """
    print("\n正在检查 Ollama 健康状态...")
    
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Ollama 服务运行正常")
            return True
        else:
            print(f"⚠️  非标准响应: {response.status_code}")
            return False
    except:
        print("❌ 无法访问根路径")
        return False

if __name__ == "__main__":
    # 可以修改这里的地址，如果是远程服务器改成对应的IP
    OLLAMA_BASE_URL = "http://LAPTOP-R2FHBO1E.local:11434"
    
    print("=" * 50)
    print("Ollama 服务连通性测试")
    print("=" * 50)
    
    # 执行所有测试
    tests_passed = 0
    tests_total = 0
    
    # 测试1: 基础连接
    tests_total += 1
    if test_ollama_connection(OLLAMA_BASE_URL):
        tests_passed += 1
    
    # 测试2: 健康状态
    tests_total += 1
    if test_health_status(OLLAMA_BASE_URL):
        tests_passed += 1
    
    # 测试3: 聊天功能（修改为你实际有的模型）
    tests_total += 1
    # 尝试多个可能的模型名称
    available_models = ["qwen3:4b"]
    
    model_working = None
    for model in available_models:
        if test_chat_model(OLLAMA_BASE_URL, model):
            model_working = model
            tests_passed += 1
            break
        else:
            print(f"模型 {model} 不可用，尝试下一个...\n")
    
    if model_working:
        print(f"\n✅ 找到可用的模型: {model_working}")
    else:
        print("\n❌ 没有找到可用的模型")
        print("建议执行以下命令下载模型:")
        print("  ollama pull llama3.2  # 推荐")
        print("  ollama pull llama2    # 经典")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {tests_passed}/{tests_total} 项通过")
    
    if tests_passed >= 2:
        print("✅ Ollama 基本工作正常！")
    else:
        print("❌ Ollama 配置可能有问题")
        print("\n常见问题解决:")
        print("1. 确保 Ollama 已启动: 终端运行 'ollama serve'")
        print("2. 检查端口: netstat -an | grep 11434")
        print("3. 下载模型: ollama pull llama3.2")