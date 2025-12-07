import ollama

def simple_multi_role_conversation():
    """基础多角色对话 - 角色A和角色B交替对话"""
    
    # 初始化对话历史
    conversation_history = []
    
    # 定义角色
    roles = {
        'Alice': '你是一个乐观开朗的朋友，总是积极思考',
        'Bob': '你是一个理性谨慎的朋友，喜欢分析问题'
    }
    
    # 起始话题
    topic = "讨论人工智能对未来工作的影响"
    
    # Alice 开始对话
    print("=== 多角色对话开始 ===")
    
    for round_num in range(3):  # 进行3轮对话
        for role_name, role_prompt in roles.items():
            # 构建系统提示
            system_message = f"{role_prompt}\n当前话题: {topic}\n"
            
            # 如果之前有对话，添加到历史
            if conversation_history:
                system_message += "之前的对话:\n"
                for msg in conversation_history[-2:]:  # 只保留最近2条
                    system_message += f"{msg['role']}: {msg['content']}\n"
            
            # 生成回复
            response = ollama.chat(
                model='llama3.2',  # 替换为你的模型
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': f'请以{role_name}的身份继续对话'}
                ]
            )
            
            reply = response['message']['content']
            print(f"\n{role_name}: {reply}")
            
            # 保存到历史
            conversation_history.append({
                'role': role_name,
                'content': reply
            })

# 使用示例
simple_multi_role_conversation()