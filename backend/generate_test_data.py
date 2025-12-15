#!/usr/bin/env python3
"""
教育知识图谱模拟数据生成脚本

生成符合实体模型规范的真实模拟数据，包括至少40个学生节点
以及相关的教师、课程、知识点和错误类型节点，
并生成节点间的关系数据。
"""

import asyncio
from datetime import datetime, timedelta
from faker import Faker
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType
from app.services.graph_service import GraphManagementService

# 初始化Faker实例
fake = Faker('zh_CN')

class KnowledgeGraphDataGenerator:
    """知识图谱数据生成器"""
    
    def __init__(self):
        self.graph_service = GraphManagementService()
        self.fake = fake
        self.generated_data = {
            'students': [],
            'teachers': [],
            'courses': [],
            'knowledge_points': [],
            'error_types': []
        }
    
    async def generate_students(self, count=40):
        """生成学生节点数据"""
        print(f"📚 开始生成{count}个学生节点...")
        
        majors = ["计算机科学与技术", "软件工程", "人工智能", "数据科学", "信息安全", "网络工程"]
        grades = ["大一", "大二", "大三", "大四"]
        
        for i in range(count):
            student_id = f"S{20200000 + i + 1}"  # 生成学号
            name = self.fake.name()
            age = self.fake.random_int(min=18, max=24)
            gender = self.fake.random_element(elements=(["male"] * 6 + ["female"] * 4))
            grade = self.fake.random_element(elements=grades)
            major = self.fake.random_element(elements=majors)
            
            # 生成符合StudentNodeProperties要求的完整嵌套数据结构
            student = await self.graph_service.create_node(
                node_type=NodeType.STUDENT,
                properties={
                    "student_id": student_id,
                    "name": name,
                    "major": major,
                    "enrollment_date": (datetime.now() - timedelta(days=self.fake.random_int(min=365, max=1460))),
                    "last_updated": datetime.now(),
                    "profile_completeness": round(self.fake.pyfloat(min_value=0.7, max_value=1.0), 2),
                    "data_version": "1.0",
                    "metadata": {"source": "mock_data", "generated_at": datetime.now().isoformat()},
                    
                    # 基本信息维度
                    "basic_info": {
                        "age": age,
                        "gender": gender,
                        "school": "北京科技大学",
                        "grade": grade
                    },
                    
                    # 先前知识储备维度
                    "prior_knowledge": {
                        "elementary": self.fake.random_int(min=60, max=95),
                        "junior_high": self.fake.random_int(min=50, max=90),
                        "senior_high": self.fake.random_int(min=40, max=85),
                        "university": self.fake.random_int(min=30, max=80),
                        "professional": self.fake.random_int(min=20, max=75),
                        "assessment_date": datetime.now() - timedelta(days=self.fake.random_int(min=1, max=30))
                    },
                    
                    # 学习投入维度
                    "learning_engagement": {
                        "emotional_engagement": {
                            "interest": self.fake.random_int(min=2, max=5),
                            "enjoyment": self.fake.random_int(min=2, max=5),
                            "satisfaction": self.fake.random_int(min=2, max=5)
                        },
                        "behavioral_engagement": {
                            "participation": self.fake.random_int(min=2, max=5),
                            "effort": self.fake.random_int(min=2, max=5),
                            "persistence": self.fake.random_int(min=2, max=5)
                        },
                        "cognitive_engagement": {
                            "deep_thinking": self.fake.random_int(min=2, max=5),
                            "strategic_learning": self.fake.random_int(min=2, max=5),
                            "self_regulation": self.fake.random_int(min=2, max=5)
                        }
                    },
                    
                    # 学习风格维度
                    "learning_style": {
                        "visual_auditory": self.fake.random_int(min=-5, max=5),
                        "verbal_nonverbal": self.fake.random_int(min=-5, max=5),
                        "active_reflective": self.fake.random_int(min=-5, max=5),
                        "sensing_intuitive": self.fake.random_int(min=-5, max=5),
                        "sequential_global": self.fake.random_int(min=-5, max=5),
                        "inductive_deductive": self.fake.random_int(min=-5, max=5),
                        "cooperative_competitive": self.fake.random_int(min=-5, max=5),
                        "structured_flexible": self.fake.random_int(min=-5, max=5),
                        "concrete_abstract": self.fake.random_int(min=-5, max=5),
                        "field_dependent_independent": self.fake.random_int(min=-5, max=5),
                        "impulsive_reflective": self.fake.random_int(min=-5, max=5)
                    },
                    
                    # 认知负荷维度
                    "cognitive_load": {
                        "extraneous": {
                            "interface_complexity": self.fake.random_int(min=1, max=4),
                            "information_overload": self.fake.random_int(min=1, max=4),
                            "distraction_level": self.fake.random_int(min=1, max=4),
                            "task_irrelevance": self.fake.random_int(min=1, max=4),
                            "presentation_clarity": self.fake.random_int(min=2, max=5)
                        },
                        "intrinsic": {
                            "task_difficulty": self.fake.random_int(min=2, max=5),
                            "concept_complexity": self.fake.random_int(min=2, max=5),
                            "mental_effort": self.fake.random_int(min=2, max=5)
                        }
                    },
                    
                    # 学习动机维度
                    "learning_motivation": {
                        "intrinsic_motivation": self.fake.random_int(min=2, max=5),
                        "extrinsic_motivation": self.fake.random_int(min=2, max=5),
                        "achievement_motivation": self.fake.random_int(min=2, max=5),
                        "social_motivation": self.fake.random_int(min=1, max=5),
                        "avoidance_motivation": self.fake.random_int(min=1, max=4)
                    },
                    
                    # 高阶思维维度
                    "higher_order_thinking": {
                        "abstraction": {
                            "pattern_recognition": self.fake.random_int(min=2, max=5),
                            "conceptualization": self.fake.random_int(min=2, max=5),
                            "generalization": self.fake.random_int(min=2, max=5),
                            "symbolization": self.fake.random_int(min=2, max=5)
                        },
                        "decomposition": {
                            "problem_breakdown": self.fake.random_int(min=2, max=5),
                            "structural_analysis": self.fake.random_int(min=2, max=5),
                            "component_identification": self.fake.random_int(min=2, max=5)
                        },
                        "algorithmic_thinking": {
                            "sequential_logic": self.fake.random_int(min=2, max=5),
                            "conditional_reasoning": self.fake.random_int(min=2, max=5),
                            "iterative_thinking": self.fake.random_int(min=2, max=5),
                            "optimization_mindset": self.fake.random_int(min=2, max=5)
                        },
                        "evaluation": {
                            "critical_analysis": self.fake.random_int(min=2, max=5),
                            "evidence_assessment": self.fake.random_int(min=2, max=5),
                            "quality_judgment": self.fake.random_int(min=2, max=5),
                            "validity_checking": self.fake.random_int(min=2, max=5)
                        },
                        "generalization": {
                            "transfer_learning": self.fake.random_int(min=2, max=5),
                            "analogical_reasoning": self.fake.random_int(min=2, max=5),
                            "principle_extraction": self.fake.random_int(min=2, max=5),
                            "application_scope": self.fake.random_int(min=2, max=5)
                        }
                    },
                    
                    # 人机信任度维度
                    "human_ai_trust": {
                        "reliability_trust": self.fake.random_int(min=2, max=5),
                        "competence_trust": self.fake.random_int(min=2, max=5),
                        "predictability_trust": self.fake.random_int(min=2, max=5),
                        "transparency_trust": self.fake.random_int(min=2, max=5),
                        "benevolence_trust": self.fake.random_int(min=2, max=5),
                        "overall_trust": self.fake.random_int(min=2, max=5)
                    },
                    
                    # 学习方法倾向维度
                    "learning_method_preference": {
                        "deep_learning": {
                            "meaning_construction": self.fake.random_int(min=2, max=5),
                            "critical_thinking": self.fake.random_int(min=2, max=5),
                            "connection_making": self.fake.random_int(min=2, max=5),
                            "reflective_practice": self.fake.random_int(min=2, max=5)
                        },
                        "strategic_learning": {
                            "goal_setting": self.fake.random_int(min=2, max=5),
                            "planning_organization": self.fake.random_int(min=2, max=5),
                            "monitoring_regulation": self.fake.random_int(min=2, max=5),
                            "resource_management": self.fake.random_int(min=2, max=5)
                        },
                        "surface_learning": {
                            "memorization": self.fake.random_int(min=1, max=4),
                            "repetition_practice": self.fake.random_int(min=1, max=4),
                            "passive_reception": self.fake.random_int(min=1, max=4),
                            "minimum_effort": self.fake.random_int(min=1, max=4)
                        }
                    },
                    
                    # 学习态度维度
                    "learning_attitude": {
                        "enjoyment": self.fake.random_int(min=2, max=5),
                        "confidence": self.fake.random_int(min=2, max=5)
                    },
                    
                    # 学习行为数据维度
                    "learning_behavior_data": {
                        "ai_interaction_count": self.fake.random_int(min=10, max=200),
                        "error_execution_count": self.fake.random_int(min=5, max=100),
                        "session_duration": self.fake.random_int(min=30, max=300),
                        "resource_access_count": self.fake.random_int(min=5, max=150),
                        "help_seeking_frequency": self.fake.random_int(min=0, max=50),
                        "task_completion_rate": round(self.fake.pyfloat(min_value=0.5, max_value=1.0), 2),
                        "last_active_date": datetime.now() - timedelta(days=self.fake.random_int(min=0, max=14))
                    }
                }
            )
            
            # 保存生成的学生数据
            self.generated_data['students'].append(student)
            print(f"   ✓ 创建学生: {student.properties['name']} (ID: {student.id})")
        
        print(f"✅ 已生成{count}个学生节点")
    
    async def generate_teachers(self, count=6):
        """生成教师节点数据"""
        print(f"👨‍🏫 开始生成{count}个教师节点...")
        
        subjects = ["计算机科学", "软件工程", "人工智能", "数据科学", "信息安全", "网络工程", "机器学习", "深度学习"]
        
        for i in range(count):
            teacher = await self.graph_service.create_node(
                node_type=NodeType.TEACHER,
                properties={
                    "teacher_id": f"T{2010000 + i + 1}",  # 生成教师ID
                    "name": self.fake.name(),
                    "subject": self.fake.random_element(elements=subjects)
                }
            )
            
            # 保存生成的教师数据
            self.generated_data['teachers'].append(teacher)
            print(f"   ✓ 创建教师: {teacher.properties['name']} (ID: {teacher.id})")
        
        print(f"✅ 已生成{count}个教师节点")
    
    async def generate_courses(self, count=12):
        """生成课程节点数据"""
        print(f"📖 开始生成{count}个课程节点...")
        
        course_names = [
            "Python程序设计",
            "数据结构与算法",
            "数据库原理",
            "计算机网络",
            "操作系统",
            "人工智能基础",
            "机器学习",
            "深度学习",
            "自然语言处理",
            "计算机视觉",
            "大数据技术",
            "信息安全导论",
            "软件工程导论",
            "网络编程",
            "算法设计与分析"
        ]
        
        for i in range(min(count, len(course_names))):
            course = await self.graph_service.create_node(
                node_type=NodeType.COURSE,
                properties={
                    "course_id": f"C{2023000 + i + 1}",  # 生成课程ID
                    "name": course_names[i],
                    "description": self.fake.text(max_nb_chars=200),
                    "difficulty": self.fake.random_element(elements=["beginner", "intermediate", "advanced"])
                }
            )
            
            # 保存生成的课程数据
            self.generated_data['courses'].append(course)
            print(f"   ✓ 创建课程: {course.properties['name']} (ID: {course.id})")
        
        print(f"✅ 已生成{count}个课程节点")
    
    async def generate_knowledge_points(self, count=25):
        """生成知识点节点数据"""
        print(f"💡 开始生成{count}个知识点节点...")
        
        categories = ["编程基础", "数据结构", "算法", "数据库", "网络", "人工智能", "机器学习", "深度学习"]
        
        for i in range(count):
            knowledge_point = await self.graph_service.create_node(
                node_type=NodeType.KNOWLEDGE_POINT,
                properties={
                    "knowledge_point_id": f"KP{2023000 + i + 1}",  # 生成知识点ID
                    "name": self.fake.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None),
                    "description": self.fake.text(max_nb_chars=100),
                    "category": self.fake.random_element(elements=categories)
                }
            )
            
            # 保存生成的知识点数据
            self.generated_data['knowledge_points'].append(knowledge_point)
            print(f"   ✓ 创建知识点: {knowledge_point.properties['name']} (ID: {knowledge_point.id})")
        
        print(f"✅ 已生成{count}个知识点节点")
    
    async def generate_error_types(self, count=12):
        """生成错误类型节点数据"""
        print(f"❌ 开始生成{count}个错误类型节点...")
        
        error_names = [
            "语法错误",
            "逻辑错误",
            "运行时错误",
            "类型错误",
            "索引错误",
            "键错误",
            "属性错误",
            "名称错误",
            "值错误",
            "断言错误",
            "导入错误",
            "模块未找到错误"
        ]
        
        for i in range(min(count, len(error_names))):
            error_type = await self.graph_service.create_node(
                node_type=NodeType.ERROR_TYPE,
                properties={
                    "error_type_id": f"ET{2023000 + i + 1}",  # 生成错误类型ID
                    "name": error_names[i],
                    "description": self.fake.text(max_nb_chars=100),
                    "severity": self.fake.random_element(elements=["low", "medium", "high"])
                }
            )
            
            # 保存生成的错误类型数据
            self.generated_data['error_types'].append(error_type)
            print(f"   ✓ 创建错误类型: {error_type.properties['name']} (ID: {error_type.id})")
        
        print(f"✅ 已生成{count}个错误类型节点")
    
    async def generate_teaches_relationships(self):
        """生成教师教授课程的关系"""
        print("🔗 开始生成TEACHES关系...")
        
        teachers = self.generated_data['teachers']
        courses = self.generated_data['courses'].copy()
        
        # 为每位教师分配2-4门课程，但确保不超过剩余课程数量
        for teacher in teachers:
            # 根据剩余课程数量动态调整分配数量
            available_courses_count = len(courses)
            if available_courses_count == 0:
                break
                
            # 计算可分配的最大课程数
            max_assignable = min(4, available_courses_count)
            min_assignable = min(2, max_assignable)
            
            # 随机选择2-4门课程（但不超过剩余课程数量）
            assign_count = self.fake.random_int(min=min_assignable, max=max_assignable)
            assigned_courses = self.fake.random_sample(elements=courses, length=assign_count)
            
            for course in assigned_courses:
                # 生成TEACHES关系
                relationship = await self.graph_service.create_relationship(
                    from_node_id=teacher.id,
                    to_node_id=course.id,
                    relationship_type=RelationshipType.TEACHES,
                    properties={
                        "interaction_count": self.fake.random_int(min=1, max=100),
                        "last_interaction_date": datetime.now().isoformat()
                    }
                )
                
                # 从课程列表中移除已分配的课程，避免重复分配
                courses.remove(course)
                print(f"   ✓ {teacher.properties['name']} 教授 {course.properties['name']}")
        
        print("✅ 已生成TEACHES关系")
    
    async def generate_learns_relationships(self):
        """生成学生学习课程的关系"""
        print("🔗 开始生成LEARNS关系...")
        
        students = self.generated_data['students']
        courses = self.generated_data['courses']  # 使用已生成的课程数据
        
        # 为每位学生分配3-6门课程
        for student in students:
            # 随机选择3-6门课程
            max_courses = min(len(courses), 6)
            min_courses = min(max_courses, 3)
            num_courses = self.fake.random_int(min=min_courses, max=max_courses)
            selected_courses = self.fake.random_sample(elements=courses, length=num_courses)
            
            for course in selected_courses:
                # 生成LEARNS关系
                relationship = await self.graph_service.create_relationship(
                    from_node_id=student.id,
                    to_node_id=course.id,
                    relationship_type=RelationshipType.LEARNS,
                    properties={
                        "enrollment_date": (datetime.now() - timedelta(days=self.fake.random_int(min=30, max=365))).isoformat(),
                        "progress": round(self.fake.pyfloat(min_value=0.1, max_value=1.0), 2) * 100,  # 转换为百分比
                        "time_spent": self.fake.random_int(min=10, max=200)
                    }
                )
                print(f"   ✓ {student.properties['name']} 学习 {course.properties['name']}")
        
        print("✅ 已生成LEARNS关系")
    
    async def generate_contains_relationships(self):
        """生成课程包含知识点的关系"""
        print("🔗 开始生成CONTAINS关系...")
        
        courses = self.generated_data['courses']
        knowledge_points = self.generated_data['knowledge_points']
        
        # 为每门课程分配2-5个知识点
        for course in courses:
            # 随机选择2-5个知识点
            max_kps = min(len(knowledge_points), 5)
            min_kps = min(max_kps, 2)
            num_kps = self.fake.random_int(min=min_kps, max=max_kps)
            selected_kps = self.fake.random_sample(elements=knowledge_points, length=num_kps)
            
            for i, kp in enumerate(selected_kps):
                # 生成CONTAINS关系
                relationship = await self.graph_service.create_relationship(
                    from_node_id=course.id,
                    to_node_id=kp.id,
                    relationship_type=RelationshipType.CONTAINS,
                    properties={
                        "order": i + 1,
                        "importance": self.fake.random_element(elements=["core", "supplementary"])
                    }
                )
                print(f"   ✓ {course.properties['name']} 包含 {kp.properties['name']}")
        
        print("✅ 已生成CONTAINS关系")
    
    async def generate_has_error_relationships(self):
        """生成知识点关联错误类型的关系"""
        print("🔗 开始生成HAS_ERROR关系...")
        
        knowledge_points = self.generated_data['knowledge_points']
        error_types = self.generated_data['error_types']
        
        # 为每个知识点关联1-3种错误类型
        for kp in knowledge_points:
            # 随机选择1-3种错误类型
            max_ets = min(len(error_types), 3)
            min_ets = min(max_ets, 1)
            num_ets = self.fake.random_int(min=min_ets, max=max_ets)
            selected_ets = self.fake.random_sample(elements=error_types, length=num_ets)
            
            for et in selected_ets:
                # 生成HAS_ERROR关系
                relationship = await self.graph_service.create_relationship(
                    from_node_id=kp.id,
                    to_node_id=et.id,
                    relationship_type=RelationshipType.HAS_ERROR,
                    properties={
                        "occurrence_count": self.fake.random_int(min=1, max=50),
                        "first_occurrence": (datetime.now() - timedelta(days=self.fake.random_int(min=30, max=365))).isoformat(),
                        "last_occurrence": datetime.now().isoformat(),
                        "course_id": f"C{2023000 + self.fake.random_int(min=1, max=12)}",  # 随机课程ID
                        "resolved": self.fake.boolean(chance_of_getting_true=30)  # 30%的错误已解决
                    }
                )
                print(f"   ✓ {kp.properties['name']} 关联 {et.properties['name']}")
        
        print("✅ 已生成HAS_ERROR关系")
    
    async def generate_chat_with_relationships(self):
        """生成学生之间聊天互动的关系"""
        print("💬 开始生成CHAT_WITH关系...")
        
        students = self.generated_data['students']
        
        # 生成学生之间的聊天关系
        for _ in range(self.fake.random_int(min=50, max=100)):
            # 随机选择两个不同的学生
            student1, student2 = self.fake.random_sample(elements=students, length=2)
            
            # 生成CHAT_WITH关系
            relationship = await self.graph_service.create_relationship(
                from_node_id=student1.id,
                to_node_id=student2.id,
                relationship_type=RelationshipType.CHAT_WITH,
                properties={
                    "message_count": self.fake.random_int(min=1, max=50),
                    "last_interaction_date": datetime.now().isoformat(),
                    "topics": self.fake.random_sample(
                        elements=["课程讨论", "作业帮助", "考试复习", "项目合作", "技术交流"],
                        length=self.fake.random_int(min=1, max=3)
                    )
                }
            )
            print(f"   ✓ {student1.properties['name']} 与 {student2.properties['name']} 聊天互动")
        
        print("✅ 已生成CHAT_WITH关系")
    
    async def generate_likes_relationships(self):
        """生成学生之间点赞互动的关系"""
        print("👍 开始生成LIKES关系...")
        
        students = self.generated_data['students']
        
        # 生成学生之间的点赞关系
        for _ in range(self.fake.random_int(min=80, max=150)):
            # 随机选择两个不同的学生
            student1, student2 = self.fake.random_sample(elements=students, length=2)
            
            # 生成LIKES关系
            relationship = await self.graph_service.create_relationship(
                from_node_id=student1.id,
                to_node_id=student2.id,
                relationship_type=RelationshipType.LIKES,
                properties={
                    "like_count": self.fake.random_int(min=1, max=10),
                    "last_like_date": datetime.now().isoformat()
                }
            )
            print(f"   ✓ {student1.properties['name']} 点赞 {student2.properties['name']}")
        
        print("✅ 已生成LIKES关系")
    
    async def generate_relates_to_relationships(self):
        """生成知识点之间关联的关系"""
        print("🔗 开始生成RELATES_TO关系...")
        
        knowledge_points = self.generated_data['knowledge_points']
        
        # 按类别分组知识点
        kps_by_category = {}
        for kp in knowledge_points:
            category = kp.properties.get('category')
            if category not in kps_by_category:
                kps_by_category[category] = []
            kps_by_category[category].append(kp)
        
        # 生成同类别知识点之间的关联关系
        for category, kps in kps_by_category.items():
            if len(kps) < 2:
                continue
                
            # 为每个知识点生成1-2个同类别关联
            for kp in kps:
                # 获取除当前知识点外的其他同类别知识点
                other_kps = [kp_item for kp_item in kps if kp_item.id != kp.id]
                if not other_kps:
                    continue
                    
                # 随机选择1-2个同类别知识点
                max_related = min(len(other_kps), 2)
                min_related = min(max_related, 1)
                num_related = self.fake.random_int(min=min_related, max=max_related)
                related_kps = self.fake.random_sample(elements=other_kps, length=num_related)
                
                for related_kp in related_kps:
                    # 生成RELATES_TO关系
                    relationship = await self.graph_service.create_relationship(
                        from_node_id=kp.id,
                        to_node_id=related_kp.id,
                        relationship_type=RelationshipType.RELATES_TO,
                        properties={
                            "strength": round(self.fake.pyfloat(min_value=0.5, max_value=1.0), 2),
                            "confidence": round(self.fake.pyfloat(min_value=0.7, max_value=1.0), 2)
                        }
                    )
                    print(f"   ✓ {kp.properties['name']} 关联 {related_kp.properties['name']}")
        
        print("✅ 已生成RELATES_TO关系")
    
    async def verify_data_integrity(self):
        """验证生成的数据完整性"""
        print("🔍 开始验证数据完整性...")
        
        # 检查已生成的数据数量
        print(f"📊 Student节点数量: {len(self.generated_data['students'])}")
        print(f"📊 Teacher节点数量: {len(self.generated_data['teachers'])}")
        print(f"📊 Course节点数量: {len(self.generated_data['courses'])}")
        print(f"📊 KnowledgePoint节点数量: {len(self.generated_data['knowledge_points'])}")
        print(f"📊 ErrorType节点数量: {len(self.generated_data['error_types'])}")
        
        # 检查学生数量是否符合要求
        if len(self.generated_data['students']) < 40:
            print("❌ 学生节点数量不足，需要至少40个")
            return False
        
        print("✅ 数据完整性验证完成")
        return True
    
    async def generate_all_data(self):
        """生成所有数据"""
        print("🚀 开始生成知识图谱模拟数据...")
        
        # 清空数据库 - 使用直接的Cypher查询
        from app.database import neo4j_connection
        async with neo4j_connection.get_session() as session:
            await session.run("MATCH (n) DETACH DELETE n")
        print("✅ 已清空数据库")
        
        # 生成节点数据
        await self.generate_students(count=45)  # 生成45个学生节点
        await self.generate_teachers(count=7)   # 生成7个教师节点
        await self.generate_courses(count=14)   # 生成14个课程节点
        await self.generate_knowledge_points(count=28)  # 生成28个知识点节点
        await self.generate_error_types(count=12)  # 生成12个错误类型节点
        
        # 生成关系数据
        await self.generate_teaches_relationships()
        await self.generate_learns_relationships()
        await self.generate_contains_relationships()
        await self.generate_has_error_relationships()
        await self.generate_chat_with_relationships()
        await self.generate_likes_relationships()
        await self.generate_relates_to_relationships()
        
        # 验证数据完整性
        await self.verify_data_integrity()
        
        print("🎉 知识图谱模拟数据生成完成！")


async def main():
    """主函数"""
    generator = KnowledgeGraphDataGenerator()
    
    try:
        # 生成所有数据
        await generator.generate_all_data()
        
    except Exception as e:
        print(f"❌ 数据生成失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
