# 问卷问题与认知维度映射关系

## 1. 认知维度列表

| 维度编号 | 认知维度 | 子维度（如果有） |
| :--- | :--- | :--- |
| 1 | 基本信息 | - |
| 2 | 知识储备 | - |
| 3 | 学习动机 | - |
| 4 | 学习态度 | 享受度、自信心 |
| 5 | 学习投入 | 认知投入 |
| 6 | 自我调节学习 | - |
| 7 | 计算思维 | 评价 |
| 8 | 学习方法倾向 | 深度学习方法 |
| 9 | 认知负荷 | 内部认知负荷 |
| 10 | 人机信任度 | - |
| 11 | 人工智能素养 | - |

## 2. 详细映射关系

### 2.1 基本信息

**对应问卷问题：**
- Q1: 性别 ○男 ○女
- Q2: 我喜欢 A．和他人一起学习 B. 独自学习
- Q3: 我的性格偏 A．外向 B.内向
- Q4: 在学习小组遇到难题时，我通常会 A．挺身而出，畅所欲言 B. 保持安静，倾听意见

**测量目标：** 收集学习者的基本人口统计学信息和学习偏好。

### 2.2 知识储备

**对应问卷问题：**
- Q11-1: 我大致了解数据的概念。
- Q11-2: 我大致了解算法的概念。
- Q11-3: 我大致了解网络的概念。
- Q11-4: 我大致了解信息处理的概念。
- Q11-5: 我大致了解信息安全的概念。
- Q11-6: 我大致了解人工智能的概念。

**测量目标：** 评估学习者对信息科技相关概念的了解程度。

### 2.3 学习动机

**对应问卷问题：**
- Q5-1: 我觉得信息课很有意思。
- Q5-2: 我觉得信息课上所学内容很有用。
- Q5-3: 我希望在信息课上学到更多知识和技能。

**测量目标：** 了解学习者对信息科技课程的学习动机和兴趣程度。

### 2.4 学习态度

**子维度：享受度**
- Q6-1: 我喜欢信息课。

**子维度：自信心**
- Q6-2: 我学习信息课的态度很积极。
- Q6-3: 我对信息课很感兴趣。

**测量目标：** 评估学习者对信息科技课程的态度和自信心。

### 2.5 学习投入

**子维度：认知投入**
- Q7-1: 信息课上，我会将新学内容和已有知识相关联。
- Q7-2: 我会思考课程内容在生活中的用处。
- Q7-3: 信息课上，我会努力表达我的想法。

**测量目标：** 了解学习者在信息科技课程中的认知投入程度。

### 2.6 自我调节学习

**对应问卷问题：**
- Q8-1: 我会为自己设定学习目标，确定学习方式。
- Q8-2: 我会通过自我提问来促进学习。
- Q8-3: 在遇到问题时，我会尝试努力解决它。

**测量目标：** 评估学习者的自我调节学习能力。

### 2.7 计算思维

**子维度：评价**
- Q9-1: 遇到问题时，我会努力去找办法解决。
- Q9-2: 我会为问题解决找出最佳方法。
- Q9-3: 我会想出快速解决问题的方法。

**测量目标：** 评估学习者的计算思维能力，特别是问题解决的评价能力。

### 2.8 学习方法倾向

**子维度：深度学习方法**
- Q10-1: 在阅读教材时，我会思考编写者的意图。
- Q10-2: 在阅读教材时，我会思考各部分内容的关系。
- Q10-3: 在完成学习活动时，我会思考老师安排活动的意图。

**测量目标：** 了解学习者的学习方法倾向，特别是深度学习方法的使用情况。

### 2.9 认知负荷

**子维度：内部认知负荷**
- Q12-1: 我需要很多努力才能听懂老师的讲解。
- Q12-2: 我需要很多努力才能完成课程任务。
- Q12-3: 我需要很多努力才能学好信息课。

**测量目标：** 评估学习者在信息科技课程中的认知负荷程度。

### 2.10 人机信任度

**对应问卷问题：**
- Q13-1: 我认为人工智能会提供隐私保护等安全保障。
- Q13-2: 我认为人工智能很可靠。
- Q13-3: 我很信任人工智能。

**测量目标：** 了解学习者对人工智能的信任程度。

### 2.11 人工智能素养

**对应问卷问题：**
- Q14-1: 我知道人类和人工智能各自的优缺点。
- Q14-2: 我知道人工智能会替代人类的部分工作。
- Q14-3: 我知道人工智能也会带来新的工作机会。
- Q14-4: 我能规范地使用人工智能（如不用它替代做作业）。
- Q14-5: 我能有效使用人工智能辅助完成任务。
- Q14-6: 我能利用人工智能与同伴进行更好地交流与合作。
- Q14-7: 我知道人工智能可能带来隐私泄露等风险。
- Q14-8: 我能初步理解人工智能与人类的关系。

**测量目标：** 评估学习者的人工智能素养水平。

## 3. 数据结构设计

### 3.1 学习者认知模板数据结构

```javascript
{
  "learnerId": "唯一标识符",
  "basicInfo": {
    "gender": "性别",
    "learningPreference": "学习偏好",
    "personality": "性格倾向",
    "groupBehavior": "小组行为"
  },
  "knowledgeReserve": {
    "dataConcept": "数据概念了解程度",
    "algorithmConcept": "算法概念了解程度",
    "networkConcept": "网络概念了解程度",
    "informationProcessing": "信息处理概念了解程度",
    "informationSecurity": "信息安全概念了解程度",
    "aiConcept": "人工智能概念了解程度"
  },
  "learningMotivation": {
    "interest": "课程兴趣",
    "usefulness": "内容有用性",
    "expectation": "学习期望"
  },
  "learningAttitude": {
    "enjoyment": "享受度",
    "confidence": "自信心",
    "interest": "兴趣程度"
  },
  "learningEngagement": {
    "cognitiveEngagement": [
      "新旧知识关联",
      "生活应用思考",
      "表达想法"
    ]
  },
  "selfRegulatedLearning": [
    "设定学习目标",
    "自我提问",
    "问题解决"
  ],
  "computationalThinking": {
    "evaluation": [
      "努力解决问题",
      "寻找最佳方法",
      "快速解决问题"
    ]
  },
  "learningApproach": {
    "deepLearning": [
      "思考编写者意图",
      "思考内容关系",
      "思考活动意图"
    ]
  },
  "cognitiveLoad": {
    "internalLoad": [
      "听懂讲解的努力",
      "完成任务的努力",
      "学好课程的努力"
    ]
  },
  "humanMachineTrust": [
    "隐私保护信任",
    "可靠性信任",
    "整体信任"
  ],
  "aiLiteracy": [
    "优缺点认知",
    "工作替代认知",
    "新机会认知",
    "规范使用能力",
    "辅助使用能力",
    "交流合作能力",
    "风险认知",
    "关系理解"
  ]
}
```

### 3.2 问卷数据映射

| 问卷问题 | 映射到数据结构 |
| :--- | :--- |
| Q1 | basicInfo.gender |
| Q2 | basicInfo.learningPreference |
| Q3 | basicInfo.personality |
| Q4 | basicInfo.groupBehavior |
| Q11-1 | knowledgeReserve.dataConcept |
| Q11-2 | knowledgeReserve.algorithmConcept |
| Q11-3 | knowledgeReserve.networkConcept |
| Q11-4 | knowledgeReserve.informationProcessing |
| Q11-5 | knowledgeReserve.informationSecurity |
| Q11-6 | knowledgeReserve.aiConcept |
| Q5-1 | learningMotivation.interest |
| Q5-2 | learningMotivation.usefulness |
| Q5-3 | learningMotivation.expectation |
| Q6-1 | learningAttitude.enjoyment |
| Q6-2 | learningAttitude.confidence |
| Q6-3 | learningAttitude.interest |
| Q7-1 | learningEngagement.cognitiveEngagement[0] |
| Q7-2 | learningEngagement.cognitiveEngagement[1] |
| Q7-3 | learningEngagement.cognitiveEngagement[2] |
| Q8-1 | selfRegulatedLearning[0] |
| Q8-2 | selfRegulatedLearning[1] |
| Q8-3 | selfRegulatedLearning[2] |
| Q9-1 | computationalThinking.evaluation[0] |
| Q9-2 | computationalThinking.evaluation[1] |
| Q9-3 | computationalThinking.evaluation[2] |
| Q10-1 | learningApproach.deepLearning[0] |
| Q10-2 | learningApproach.deepLearning[1] |
| Q10-3 | learningApproach.deepLearning[2] |
| Q12-1 | cognitiveLoad.internalLoad[0] |
| Q12-2 | cognitiveLoad.internalLoad[1] |
| Q12-3 | cognitiveLoad.internalLoad[2] |
| Q13-1 | humanMachineTrust[0] |
| Q13-2 | humanMachineTrust[1] |
| Q13-3 | humanMachineTrust[2] |
| Q14-1 | aiLiteracy[0] |
| Q14-2 | aiLiteracy[1] |
| Q14-3 | aiLiteracy[2] |
| Q14-4 | aiLiteracy[3] |
| Q14-5 | aiLiteracy[4] |
| Q14-6 | aiLiteracy[5] |
| Q14-7 | aiLiteracy[6] |
| Q14-8 | aiLiteracy[7] |
```

## 4. 评分标准

- **基本信息**：分类数据，直接记录选项
- **其他维度**：采用五点李克特计分法，1~5分别为从"非常不同意"到"非常同意"

## 5. 数据采集与处理建议

1. **数据采集**：通过在线问卷或纸质问卷收集数据
2. **数据清洗**：去除无效问卷，确保数据完整性
3. **数据编码**：将分类数据转换为数字编码
4. **数据标准化**：对不同维度的数据进行标准化处理
5. **数据分析**：使用统计方法和机器学习算法分析学习者认知模板

## 6. 应用场景

- **个性化学习推荐**：基于认知模板为学习者推荐适合的学习资源
- **教学干预**：根据认知模板识别学习者的薄弱环节，提供针对性的教学干预
- **学习路径优化**：基于认知模板为学习者设计个性化的学习路径
- **教学效果评估**：通过认知模板的变化评估教学效果

## 7. 注意事项

- **隐私保护**：确保学习者个人信息的安全和隐私
- **数据质量**：确保数据采集的质量和可靠性
- **维度一致性**：确保认知维度的定义和测量在不同场景下的一致性
- **持续更新**：定期更新认知模板，以适应教育环境的变化
