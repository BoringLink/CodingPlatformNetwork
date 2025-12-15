// 生成模拟数据的Cypher脚本

// 1. 创建学生节点
CREATE (s1:Student {id: 's001', name: '学生1', student_id: 'STU001', grade: '三年级', created_at: datetime(), updated_at: datetime()})
CREATE (s2:Student {id: 's002', name: '学生2', student_id: 'STU002', grade: '四年级', created_at: datetime(), updated_at: datetime()})
CREATE (s3:Student {id: 's003', name: '学生3', student_id: 'STU003', grade: '三年级', created_at: datetime(), updated_at: datetime()})
CREATE (s4:Student {id: 's004', name: '学生4', student_id: 'STU004', grade: '五年级', created_at: datetime(), updated_at: datetime()})
CREATE (s5:Student {id: 's005', name: '学生5', student_id: 'STU005', grade: '四年级', created_at: datetime(), updated_at: datetime()})

// 2. 创建教师节点
CREATE (t1:Teacher {id: 't001', name: '教师1', teacher_id: 'TEA01', subject: '数学', created_at: datetime(), updated_at: datetime()})
CREATE (t2:Teacher {id: 't002', name: '教师2', teacher_id: 'TEA02', subject: '英语', created_at: datetime(), updated_at: datetime()})

// 3. 创建课程节点
CREATE (c1:Course {id: 'c001', name: '数学课程', course_id: 'COURSE01', description: '三年级数学课程', created_at: datetime(), updated_at: datetime()})
CREATE (c2:Course {id: 'c002', name: '英语课程', course_id: 'COURSE02', description: '四年级英语课程', created_at: datetime(), updated_at: datetime()})
CREATE (c3:Course {id: 'c003', name: '科学课程', course_id: 'COURSE03', description: '五年级科学课程', created_at: datetime(), updated_at: datetime()})

// 4. 创建知识点节点
CREATE (kp1:KnowledgePoint {id: 'kp001', name: '加法运算', knowledge_point_id: 'KP001', difficulty: '简单', created_at: datetime(), updated_at: datetime()})
CREATE (kp2:KnowledgePoint {id: 'kp002', name: '乘法运算', knowledge_point_id: 'KP002', difficulty: '中等', created_at: datetime(), updated_at: datetime()})
CREATE (kp3:KnowledgePoint {id: 'kp003', name: '语法结构', knowledge_point_id: 'KP003', difficulty: '中等', created_at: datetime(), updated_at: datetime()})
CREATE (kp4:KnowledgePoint {id: 'kp004', name: '阅读理解', knowledge_point_id: 'KP004', difficulty: '困难', created_at: datetime(), updated_at: datetime()})
CREATE (kp5:KnowledgePoint {id: 'kp005', name: '物理实验', knowledge_point_id: 'KP005', difficulty: '中等', created_at: datetime(), updated_at: datetime()})
CREATE (kp6:KnowledgePoint {id: 'kp006', name: '化学元素', knowledge_point_id: 'KP006', difficulty: '困难', created_at: datetime(), updated_at: datetime()})

// 5. 创建错误类型节点
CREATE (et1:ErrorType {id: 'et001', name: '计算错误', error_type_id: 'ET001', description: '数学计算错误', created_at: datetime(), updated_at: datetime()})
CREATE (et2:ErrorType {id: 'et002', name: '语法错误', error_type_id: 'ET002', description: '英语语法错误', created_at: datetime(), updated_at: datetime()})
CREATE (et3:ErrorType {id: 'et003', name: '理解错误', error_type_id: 'ET003', description: '阅读理解错误', created_at: datetime(), updated_at: datetime()})
CREATE (et4:ErrorType {id: 'et004', name: '实验操作错误', error_type_id: 'ET004', description: '科学实验操作错误', created_at: datetime(), updated_at: datetime()})

// 6. 创建关系

// 教师教授课程 (TEACHES)
MATCH (t1:Teacher {id: 't001'}), (c1:Course {id: 'c001'}) CREATE (t1)-[:TEACHES {weight: 0.8}]->(c1)
MATCH (t1:Teacher {id: 't001'}), (c3:Course {id: 'c003'}) CREATE (t1)-[:TEACHES {weight: 0.6}]->(c3)
MATCH (t2:Teacher {id: 't002'}), (c2:Course {id: 'c002'}) CREATE (t2)-[:TEACHES {weight: 0.9}]->(c2)

// 学生学习课程 (LEARNS)
MATCH (s1:Student {id: 's001'}), (c1:Course {id: 'c001'}) CREATE (s1)-[:LEARNS {weight: 0.7}]->(c1)
MATCH (s1:Student {id: 's001'}), (c2:Course {id: 'c002'}) CREATE (s1)-[:LEARNS {weight: 0.5}]->(c2)
MATCH (s2:Student {id: 's002'}), (c2:Course {id: 'c002'}) CREATE (s2)-[:LEARNS {weight: 0.8}]->(c2)
MATCH (s2:Student {id: 's002'}), (c3:Course {id: 'c003'}) CREATE (s2)-[:LEARNS {weight: 0.6}]->(c3)
MATCH (s3:Student {id: 's003'}), (c1:Course {id: 'c001'}) CREATE (s3)-[:LEARNS {weight: 0.9}]->(c1)
MATCH (s3:Student {id: 's003'}), (c3:Course {id: 'c003'}) CREATE (s3)-[:LEARNS {weight: 0.4}]->(c3)
MATCH (s4:Student {id: 's004'}), (c1:Course {id: 'c001'}) CREATE (s4)-[:LEARNS {weight: 0.6}]->(c1)
MATCH (s4:Student {id: 's004'}), (c2:Course {id: 'c002'}) CREATE (s4)-[:LEARNS {weight: 0.7}]->(c2)
MATCH (s4:Student {id: 's004'}), (c3:Course {id: 'c003'}) CREATE (s4)-[:LEARNS {weight: 0.8}]->(c3)
MATCH (s5:Student {id: 's005'}), (c1:Course {id: 'c001'}) CREATE (s5)-[:LEARNS {weight: 0.5}]->(c1)
MATCH (s5:Student {id: 's005'}), (c2:Course {id: 'c002'}) CREATE (s5)-[:LEARNS {weight: 0.9}]->(c2)

// 学生与教师聊天 (CHAT_WITH)
MATCH (s1:Student {id: 's001'}), (t1:Teacher {id: 't001'}) CREATE (s1)-[:CHAT_WITH {weight: 0.6}]->(t1)
MATCH (s1:Student {id: 's001'}), (t2:Teacher {id: 't002'}) CREATE (s1)-[:CHAT_WITH {weight: 0.4}]->(t2)
MATCH (s2:Student {id: 's002'}), (t2:Teacher {id: 't002'}) CREATE (s2)-[:CHAT_WITH {weight: 0.7}]->(t2)
MATCH (s3:Student {id: 's003'}), (t1:Teacher {id: 't001'}) CREATE (s3)-[:CHAT_WITH {weight: 0.8}]->(t1)
MATCH (s4:Student {id: 's004'}), (t1:Teacher {id: 't001'}) CREATE (s4)-[:CHAT_WITH {weight: 0.5}]->(t1)
MATCH (s4:Student {id: 's004'}), (t2:Teacher {id: 't002'}) CREATE (s4)-[:CHAT_WITH {weight: 0.6}]->(t2)
MATCH (s5:Student {id: 's005'}), (t2:Teacher {id: 't002'}) CREATE (s5)-[:CHAT_WITH {weight: 0.9}]->(t2)

// 课程包含知识点 (CONTAINS)
MATCH (c1:Course {id: 'c001'}), (kp1:KnowledgePoint {id: 'kp001'}) CREATE (c1)-[:CONTAINS {weight: 0.9}]->(kp1)
MATCH (c1:Course {id: 'c001'}), (kp2:KnowledgePoint {id: 'kp002'}) CREATE (c1)-[:CONTAINS {weight: 0.8}]->(kp2)
MATCH (c2:Course {id: 'c002'}), (kp3:KnowledgePoint {id: 'kp003'}) CREATE (c2)-[:CONTAINS {weight: 0.9}]->(kp3)
MATCH (c2:Course {id: 'c002'}), (kp4:KnowledgePoint {id: 'kp004'}) CREATE (c2)-[:CONTAINS {weight: 0.7}]->(kp4)
MATCH (c3:Course {id: 'c003'}), (kp5:KnowledgePoint {id: 'kp005'}) CREATE (c3)-[:CONTAINS {weight: 0.8}]->(kp5)
MATCH (c3:Course {id: 'c003'}), (kp6:KnowledgePoint {id: 'kp006'}) CREATE (c3)-[:CONTAINS {weight: 0.6}]->(kp6)

// 学生在知识点上有错误 (HAS_ERROR)
MATCH (s1:Student {id: 's001'}), (kp1:KnowledgePoint {id: 'kp001'}) CREATE (s1)-[:HAS_ERROR {weight: 0.5}]->(kp1)
MATCH (s1:Student {id: 's001'}), (et1:ErrorType {id: 'et001'}) CREATE (s1)-[:HAS_ERROR {weight: 0.5}]->(et1)
MATCH (s1:Student {id: 's001'}), (kp3:KnowledgePoint {id: 'kp003'}) CREATE (s1)-[:HAS_ERROR {weight: 0.6}]->(kp3)
MATCH (s1:Student {id: 's001'}), (et2:ErrorType {id: 'et002'}) CREATE (s1)-[:HAS_ERROR {weight: 0.6}]->(et2)

MATCH (s2:Student {id: 's002'}), (kp4:KnowledgePoint {id: 'kp004'}) CREATE (s2)-[:HAS_ERROR {weight: 0.4}]->(kp4)
MATCH (s2:Student {id: 's002'}), (et3:ErrorType {id: 'et003'}) CREATE (s2)-[:HAS_ERROR {weight: 0.4}]->(et3)
MATCH (s2:Student {id: 's002'}), (kp5:KnowledgePoint {id: 'kp005'}) CREATE (s2)-[:HAS_ERROR {weight: 0.7}]->(kp5)
MATCH (s2:Student {id: 's002'}), (et4:ErrorType {id: 'et004'}) CREATE (s2)-[:HAS_ERROR {weight: 0.7}]->(et4)

MATCH (s3:Student {id: 's003'}), (kp2:KnowledgePoint {id: 'kp002'}) CREATE (s3)-[:HAS_ERROR {weight: 0.3}]->(kp2)
MATCH (s3:Student {id: 's003'}), (et1:ErrorType {id: 'et001'}) CREATE (s3)-[:HAS_ERROR {weight: 0.3}]->(et1)
MATCH (s3:Student {id: 's003'}), (kp6:KnowledgePoint {id: 'kp006'}) CREATE (s3)-[:HAS_ERROR {weight: 0.5}]->(kp6)
MATCH (s3:Student {id: 's003'}), (et4:ErrorType {id: 'et004'}) CREATE (s3)-[:HAS_ERROR {weight: 0.5}]->(et4)

MATCH (s4:Student {id: 's004'}), (kp1:KnowledgePoint {id: 'kp001'}) CREATE (s4)-[:HAS_ERROR {weight: 0.2}]->(kp1)
MATCH (s4:Student {id: 's004'}), (et1:ErrorType {id: 'et001'}) CREATE (s4)-[:HAS_ERROR {weight: 0.2}]->(et1)
MATCH (s4:Student {id: 's004'}), (kp3:KnowledgePoint {id: 'kp003'}) CREATE (s4)-[:HAS_ERROR {weight: 0.4}]->(kp3)
MATCH (s4:Student {id: 's004'}), (et2:ErrorType {id: 'et002'}) CREATE (s4)-[:HAS_ERROR {weight: 0.4}]->(et2)
MATCH (s4:Student {id: 's004'}), (kp5:KnowledgePoint {id: 'kp005'}) CREATE (s4)-[:HAS_ERROR {weight: 0.3}]->(kp5)
MATCH (s4:Student {id: 's004'}), (et4:ErrorType {id: 'et004'}) CREATE (s4)-[:HAS_ERROR {weight: 0.3}]->(et4)

MATCH (s5:Student {id: 's005'}), (kp2:KnowledgePoint {id: 'kp002'}) CREATE (s5)-[:HAS_ERROR {weight: 0.6}]->(kp2)
MATCH (s5:Student {id: 's005'}), (et1:ErrorType {id: 'et001'}) CREATE (s5)-[:HAS_ERROR {weight: 0.6}]->(et1)
MATCH (s5:Student {id: 's005'}), (kp4:KnowledgePoint {id: 'kp004'}) CREATE (s5)-[:HAS_ERROR {weight: 0.5}]->(kp4)
MATCH (s5:Student {id: 's005'}), (et3:ErrorType {id: 'et003'}) CREATE (s5)-[:HAS_ERROR {weight: 0.5}]->(et3)

// 知识点之间的关联 (RELATES_TO)
MATCH (kp1:KnowledgePoint {id: 'kp001'}), (kp2:KnowledgePoint {id: 'kp002'}) CREATE (kp1)-[:RELATES_TO {weight: 0.8}]->(kp2)
MATCH (kp3:KnowledgePoint {id: 'kp003'}), (kp4:KnowledgePoint {id: 'kp004'}) CREATE (kp3)-[:RELATES_TO {weight: 0.7}]->(kp4)
MATCH (kp5:KnowledgePoint {id: 'kp005'}), (kp6:KnowledgePoint {id: 'kp006'}) CREATE (kp5)-[:RELATES_TO {weight: 0.6}]->(kp6)
MATCH (kp2:KnowledgePoint {id: 'kp002'}), (kp5:KnowledgePoint {id: 'kp005'}) CREATE (kp2)-[:RELATES_TO {weight: 0.5}]->(kp5)
MATCH (kp4:KnowledgePoint {id: 'kp004'}), (kp6:KnowledgePoint {id: 'kp006'}) CREATE (kp4)-[:RELATES_TO {weight: 0.4}]->(kp6)

// 学生点赞教师 (LIKES)
MATCH (s1:Student {id: 's001'}), (t1:Teacher {id: 't001'}) CREATE (s1)-[:LIKES {weight: 0.7}]->(t1)
MATCH (s1:Student {id: 's001'}), (t2:Teacher {id: 't002'}) CREATE (s1)-[:LIKES {weight: 0.5}]->(t2)
MATCH (s2:Student {id: 's002'}), (t2:Teacher {id: 't002'}) CREATE (s2)-[:LIKES {weight: 0.9}]->(t2)
MATCH (s3:Student {id: 's003'}), (t1:Teacher {id: 't001'}) CREATE (s3)-[:LIKES {weight: 0.8}]->(t1)
MATCH (s4:Student {id: 's004'}), (t1:Teacher {id: 't001'}) CREATE (s4)-[:LIKES {weight: 0.6}]->(t1)
MATCH (s4:Student {id: 's004'}), (t2:Teacher {id: 't002'}) CREATE (s4)-[:LIKES {weight: 0.7}]->(t2)
MATCH (s5:Student {id: 's005'}), (t2:Teacher {id: 't002'}) CREATE (s5)-[:LIKES {weight: 0.9}]->(t2)

// 返回创建的节点数量
MATCH (n) RETURN count(n) as total_nodes
