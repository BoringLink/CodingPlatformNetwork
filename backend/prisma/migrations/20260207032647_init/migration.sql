BEGIN TRY

BEGIN TRAN;

-- CreateTable
CREATE TABLE [dbo].[learning_scenarios] (
    [id] NVARCHAR(1000) NOT NULL,
    [code] NVARCHAR(1000) NOT NULL,
    [nameZh] NVARCHAR(1000) NOT NULL,
    [description] NVARCHAR(1000),
    [sortOrder] INT NOT NULL CONSTRAINT [learning_scenarios_sortOrder_df] DEFAULT 0,
    [isActive] BIT NOT NULL CONSTRAINT [learning_scenarios_isActive_df] DEFAULT 1,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [learning_scenarios_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [learning_scenarios_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [learning_scenarios_code_key] UNIQUE NONCLUSTERED ([code])
);

-- CreateTable
CREATE TABLE [dbo].[schools] (
    [id] NVARCHAR(1000) NOT NULL,
    [name] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [schools_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [schools_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [schools_name_key] UNIQUE NONCLUSTERED ([name])
);

-- CreateTable
CREATE TABLE [dbo].[grades] (
    [id] NVARCHAR(1000) NOT NULL,
    [schoolId] NVARCHAR(1000) NOT NULL,
    [gradeName] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [grades_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [grades_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [grades_schoolId_gradeName_key] UNIQUE NONCLUSTERED ([schoolId],[gradeName])
);

-- CreateTable
CREATE TABLE [dbo].[classes] (
    [id] NVARCHAR(1000) NOT NULL,
    [gradeId] NVARCHAR(1000) NOT NULL,
    [className] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [classes_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [classes_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [classes_gradeId_className_key] UNIQUE NONCLUSTERED ([gradeId],[className])
);

-- CreateTable
CREATE TABLE [dbo].[graph_nodes] (
    [id] NVARCHAR(1000) NOT NULL,
    [nodeType] NVARCHAR(1000) NOT NULL,
    [displayName] NVARCHAR(1000) NOT NULL,
    [school] NVARCHAR(1000),
    [grade] NVARCHAR(1000),
    [classId] NVARCHAR(1000),
    [isActive] BIT NOT NULL CONSTRAINT [graph_nodes_isActive_df] DEFAULT 1,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [graph_nodes_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [graph_nodes_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[student_profiles] (
    [nodeId] NVARCHAR(1000) NOT NULL,
    [learningStylePreference] NVARCHAR(1000),
    [personality] NVARCHAR(1000),
    [groupBehavior] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [student_profiles_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [student_profiles_pkey] PRIMARY KEY CLUSTERED ([nodeId])
);

-- CreateTable
CREATE TABLE [dbo].[teacher_profiles] (
    [nodeId] NVARCHAR(1000) NOT NULL,
    [subject] NVARCHAR(1000),
    [teachingGrade] NVARCHAR(1000),
    [teachingClass] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [teacher_profiles_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [teacher_profiles_pkey] PRIMARY KEY CLUSTERED ([nodeId])
);

-- CreateTable
CREATE TABLE [dbo].[knowledge_profiles] (
    [nodeId] NVARCHAR(1000) NOT NULL,
    [content] NVARCHAR(1000) NOT NULL,
    [knowledgeType] NVARCHAR(1000) NOT NULL,
    [category] NVARCHAR(1000),
    [parentNodeId] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [knowledge_profiles_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [knowledge_profiles_pkey] PRIMARY KEY CLUSTERED ([nodeId])
);

-- CreateTable
CREATE TABLE [dbo].[knowledge_relations] (
    [id] NVARCHAR(1000) NOT NULL,
    [fromKnowledgeNodeId] NVARCHAR(1000) NOT NULL,
    [toKnowledgeNodeId] NVARCHAR(1000) NOT NULL,
    [relationType] NVARCHAR(1000) NOT NULL,
    [weight] DECIMAL(5,2),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [knowledge_relations_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [knowledge_relations_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [knowledge_relations_fromKnowledgeNodeId_toKnowledgeNodeId_relationType_key] UNIQUE NONCLUSTERED ([fromKnowledgeNodeId],[toKnowledgeNodeId],[relationType])
);

-- CreateTable
CREATE TABLE [dbo].[interaction_sessions] (
    [id] NVARCHAR(1000) NOT NULL,
    [scenarioId] NVARCHAR(1000) NOT NULL,
    [sessionName] NVARCHAR(1000) NOT NULL,
    [occurredAt] DATETIME2 NOT NULL,
    [school] NVARCHAR(1000),
    [grade] NVARCHAR(1000),
    [classId] NVARCHAR(1000),
    [meta] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [interaction_sessions_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [interaction_sessions_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[interactions] (
    [id] NVARCHAR(1000) NOT NULL,
    [sessionId] NVARCHAR(1000) NOT NULL,
    [sourceNodeId] NVARCHAR(1000) NOT NULL,
    [targetNodeId] NVARCHAR(1000) NOT NULL,
    [interactionType] NVARCHAR(1000) NOT NULL,
    [strength] DECIMAL(6,3) NOT NULL,
    [actionType] NVARCHAR(1000),
    [durationSec] INT,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [interactions_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [interactions_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [interactions_sessionId_sourceNodeId_targetNodeId_interactionType_actionType_key] UNIQUE NONCLUSTERED ([sessionId],[sourceNodeId],[targetNodeId],[interactionType],[actionType])
);

-- CreateTable
CREATE TABLE [dbo].[cognitive_dimension_defs] (
    [id] NVARCHAR(1000) NOT NULL,
    [dimensionCode] NVARCHAR(1000) NOT NULL,
    [dimensionNameZh] NVARCHAR(1000) NOT NULL,
    [categoryName] NVARCHAR(1000),
    [minScore] DECIMAL(5,2) NOT NULL,
    [maxScore] DECIMAL(5,2) NOT NULL,
    [sortOrder] INT NOT NULL CONSTRAINT [cognitive_dimension_defs_sortOrder_df] DEFAULT 0,
    [isActive] BIT NOT NULL CONSTRAINT [cognitive_dimension_defs_isActive_df] DEFAULT 1,
    CONSTRAINT [cognitive_dimension_defs_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [cognitive_dimension_defs_dimensionCode_key] UNIQUE NONCLUSTERED ([dimensionCode])
);

-- CreateTable
CREATE TABLE [dbo].[student_cognitive_profiles] (
    [id] NVARCHAR(1000) NOT NULL,
    [studentNodeId] NVARCHAR(1000) NOT NULL,
    [profileVersion] NVARCHAR(1000) NOT NULL,
    [generatedAt] DATETIME2 NOT NULL,
    [totalScore] DECIMAL(6,2) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [student_cognitive_profiles_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [student_cognitive_profiles_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[student_cognitive_dimension_scores] (
    [id] NVARCHAR(1000) NOT NULL,
    [profileId] NVARCHAR(1000) NOT NULL,
    [dimensionCode] NVARCHAR(1000) NOT NULL,
    [scoreValue] DECIMAL(5,2) NOT NULL,
    [scoreLevel] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [student_cognitive_dimension_scores_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT [student_cognitive_dimension_scores_pkey] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [student_cognitive_dimension_scores_profileId_dimensionCode_key] UNIQUE NONCLUSTERED ([profileId],[dimensionCode])
);

-- CreateTable
CREATE TABLE [dbo].[legacy_students] (
    [id] NVARCHAR(1000) NOT NULL,
    [name] NVARCHAR(1000) NOT NULL,
    [school] NVARCHAR(1000) NOT NULL,
    [grade] NVARCHAR(1000) NOT NULL,
    [classId] NVARCHAR(1000) NOT NULL,
    [knowledgeReserve] FLOAT(53) NOT NULL,
    [learningEngagement] FLOAT(53) NOT NULL,
    [cognitiveLoad] FLOAT(53) NOT NULL,
    [learningMotivation] FLOAT(53) NOT NULL,
    [computationalThinking] FLOAT(53) NOT NULL,
    [humanAiTrust] FLOAT(53) NOT NULL,
    [learningMethod] FLOAT(53) NOT NULL,
    [learningAttitude] FLOAT(53) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [legacy_students_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [legacy_students_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[legacy_teachers] (
    [id] NVARCHAR(1000) NOT NULL,
    [name] NVARCHAR(1000) NOT NULL,
    [school] NVARCHAR(1000) NOT NULL,
    [teachingGrade] NVARCHAR(1000) NOT NULL,
    [teachingClass] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [legacy_teachers_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [legacy_teachers_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[legacy_teacher_class_mappings] (
    [id] NVARCHAR(1000) NOT NULL,
    [teacherId] NVARCHAR(1000) NOT NULL,
    [grade] NVARCHAR(1000) NOT NULL,
    [classId] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [legacy_teacher_class_mappings_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [legacy_teacher_class_mappings_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[legacy_knowledge_points] (
    [id] NVARCHAR(1000) NOT NULL,
    [content] NVARCHAR(1000) NOT NULL,
    [knowledgePoint] NVARCHAR(1000) NOT NULL,
    [grade] NVARCHAR(1000) NOT NULL,
    [type] NVARCHAR(1000) NOT NULL,
    [parentId] NVARCHAR(1000),
    [parentName] NVARCHAR(1000),
    [relatedKnowledgeIds] NVARCHAR(1000) NOT NULL,
    [relatedKnowledgeNames] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [legacy_knowledge_points_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [legacy_knowledge_points_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[legacy_interactions] (
    [id] NVARCHAR(1000) NOT NULL,
    [sourceId] NVARCHAR(1000) NOT NULL,
    [targetId] NVARCHAR(1000) NOT NULL,
    [sourceType] NVARCHAR(1000) NOT NULL,
    [targetType] NVARCHAR(1000) NOT NULL,
    [value] FLOAT(53) NOT NULL,
    [type] NVARCHAR(1000) NOT NULL,
    [interactionType] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [legacy_interactions_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [legacy_interactions_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateIndex
CREATE NONCLUSTERED INDEX [learning_scenarios_isActive_sortOrder_idx] ON [dbo].[learning_scenarios]([isActive], [sortOrder]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [grades_schoolId_idx] ON [dbo].[grades]([schoolId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [classes_gradeId_idx] ON [dbo].[classes]([gradeId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [graph_nodes_nodeType_idx] ON [dbo].[graph_nodes]([nodeType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [graph_nodes_school_grade_classId_idx] ON [dbo].[graph_nodes]([school], [grade], [classId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [graph_nodes_nodeType_school_grade_idx] ON [dbo].[graph_nodes]([nodeType], [school], [grade]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [knowledge_profiles_parentNodeId_idx] ON [dbo].[knowledge_profiles]([parentNodeId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [knowledge_relations_fromKnowledgeNodeId_relationType_idx] ON [dbo].[knowledge_relations]([fromKnowledgeNodeId], [relationType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [knowledge_relations_toKnowledgeNodeId_relationType_idx] ON [dbo].[knowledge_relations]([toKnowledgeNodeId], [relationType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interaction_sessions_scenarioId_occurredAt_idx] ON [dbo].[interaction_sessions]([scenarioId], [occurredAt]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interaction_sessions_school_grade_classId_occurredAt_idx] ON [dbo].[interaction_sessions]([school], [grade], [classId], [occurredAt]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_sessionId_idx] ON [dbo].[interactions]([sessionId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_sourceNodeId_targetNodeId_idx] ON [dbo].[interactions]([sourceNodeId], [targetNodeId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_targetNodeId_idx] ON [dbo].[interactions]([targetNodeId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_interactionType_createdAt_idx] ON [dbo].[interactions]([interactionType], [createdAt]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [student_cognitive_profiles_studentNodeId_generatedAt_idx] ON [dbo].[student_cognitive_profiles]([studentNodeId], [generatedAt] DESC);

-- CreateIndex
CREATE NONCLUSTERED INDEX [student_cognitive_dimension_scores_profileId_idx] ON [dbo].[student_cognitive_dimension_scores]([profileId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_students_school_grade_classId_idx] ON [dbo].[legacy_students]([school], [grade], [classId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_teachers_school_idx] ON [dbo].[legacy_teachers]([school]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_teachers_teachingGrade_teachingClass_idx] ON [dbo].[legacy_teachers]([teachingGrade], [teachingClass]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_teacher_class_mappings_teacherId_idx] ON [dbo].[legacy_teacher_class_mappings]([teacherId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_teacher_class_mappings_grade_classId_idx] ON [dbo].[legacy_teacher_class_mappings]([grade], [classId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_knowledge_points_grade_idx] ON [dbo].[legacy_knowledge_points]([grade]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_knowledge_points_type_idx] ON [dbo].[legacy_knowledge_points]([type]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_knowledge_points_parentId_idx] ON [dbo].[legacy_knowledge_points]([parentId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_interactions_sourceId_sourceType_idx] ON [dbo].[legacy_interactions]([sourceId], [sourceType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_interactions_targetId_targetType_idx] ON [dbo].[legacy_interactions]([targetId], [targetType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [legacy_interactions_type_idx] ON [dbo].[legacy_interactions]([type]);

-- AddForeignKey
ALTER TABLE [dbo].[grades] ADD CONSTRAINT [grades_schoolId_fkey] FOREIGN KEY ([schoolId]) REFERENCES [dbo].[schools]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[classes] ADD CONSTRAINT [classes_gradeId_fkey] FOREIGN KEY ([gradeId]) REFERENCES [dbo].[grades]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[student_profiles] ADD CONSTRAINT [student_profiles_nodeId_fkey] FOREIGN KEY ([nodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[teacher_profiles] ADD CONSTRAINT [teacher_profiles_nodeId_fkey] FOREIGN KEY ([nodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[knowledge_profiles] ADD CONSTRAINT [knowledge_profiles_nodeId_fkey] FOREIGN KEY ([nodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[knowledge_profiles] ADD CONSTRAINT [knowledge_profiles_parentNodeId_fkey] FOREIGN KEY ([parentNodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE [dbo].[knowledge_relations] ADD CONSTRAINT [knowledge_relations_fromKnowledgeNodeId_fkey] FOREIGN KEY ([fromKnowledgeNodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE [dbo].[knowledge_relations] ADD CONSTRAINT [knowledge_relations_toKnowledgeNodeId_fkey] FOREIGN KEY ([toKnowledgeNodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE [dbo].[interaction_sessions] ADD CONSTRAINT [interaction_sessions_scenarioId_fkey] FOREIGN KEY ([scenarioId]) REFERENCES [dbo].[learning_scenarios]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[interactions] ADD CONSTRAINT [interactions_sessionId_fkey] FOREIGN KEY ([sessionId]) REFERENCES [dbo].[interaction_sessions]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[interactions] ADD CONSTRAINT [interactions_sourceNodeId_fkey] FOREIGN KEY ([sourceNodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE [dbo].[interactions] ADD CONSTRAINT [interactions_targetNodeId_fkey] FOREIGN KEY ([targetNodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE [dbo].[student_cognitive_profiles] ADD CONSTRAINT [student_cognitive_profiles_studentNodeId_fkey] FOREIGN KEY ([studentNodeId]) REFERENCES [dbo].[graph_nodes]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[student_cognitive_dimension_scores] ADD CONSTRAINT [student_cognitive_dimension_scores_profileId_fkey] FOREIGN KEY ([profileId]) REFERENCES [dbo].[student_cognitive_profiles]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE [dbo].[student_cognitive_dimension_scores] ADD CONSTRAINT [student_cognitive_dimension_scores_dimensionCode_fkey] FOREIGN KEY ([dimensionCode]) REFERENCES [dbo].[cognitive_dimension_defs]([dimensionCode]) ON DELETE NO ACTION ON UPDATE CASCADE;

COMMIT TRAN;

END TRY
BEGIN CATCH

IF @@TRANCOUNT > 0
BEGIN
    ROLLBACK TRAN;
END;
THROW

END CATCH

