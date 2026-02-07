BEGIN TRY

BEGIN TRAN;

-- CreateTable
CREATE TABLE [dbo].[students] (
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
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [students_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [students_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[teachers] (
    [id] NVARCHAR(1000) NOT NULL,
    [name] NVARCHAR(1000) NOT NULL,
    [school] NVARCHAR(1000) NOT NULL,
    [teachingGrade] NVARCHAR(1000) NOT NULL,
    [teachingClass] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [teachers_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [teachers_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[teacher_class_mappings] (
    [id] NVARCHAR(1000) NOT NULL,
    [teacherId] NVARCHAR(1000) NOT NULL,
    [grade] NVARCHAR(1000) NOT NULL,
    [classId] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [teacher_class_mappings_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [teacher_class_mappings_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[knowledge_points] (
    [id] NVARCHAR(1000) NOT NULL,
    [content] NVARCHAR(1000) NOT NULL,
    [knowledgePoint] NVARCHAR(1000) NOT NULL,
    [grade] NVARCHAR(1000) NOT NULL,
    [type] NVARCHAR(1000) NOT NULL,
    [parentId] NVARCHAR(1000),
    [parentName] NVARCHAR(1000),
    [relatedKnowledgeIds] NVARCHAR(1000) NOT NULL,
    [relatedKnowledgeNames] NVARCHAR(1000) NOT NULL,
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [knowledge_points_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [knowledge_points_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateTable
CREATE TABLE [dbo].[interactions] (
    [id] NVARCHAR(1000) NOT NULL,
    [sourceId] NVARCHAR(1000) NOT NULL,
    [targetId] NVARCHAR(1000) NOT NULL,
    [sourceType] NVARCHAR(1000) NOT NULL,
    [targetType] NVARCHAR(1000) NOT NULL,
    [value] FLOAT(53) NOT NULL,
    [type] NVARCHAR(1000) NOT NULL,
    [interactionType] NVARCHAR(1000),
    [createdAt] DATETIME2 NOT NULL CONSTRAINT [interactions_createdAt_df] DEFAULT CURRENT_TIMESTAMP,
    [updatedAt] DATETIME2 NOT NULL,
    CONSTRAINT [interactions_pkey] PRIMARY KEY CLUSTERED ([id])
);

-- CreateIndex
CREATE NONCLUSTERED INDEX [students_school_grade_classId_idx] ON [dbo].[students]([school], [grade], [classId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [teachers_school_idx] ON [dbo].[teachers]([school]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [teachers_teachingGrade_teachingClass_idx] ON [dbo].[teachers]([teachingGrade], [teachingClass]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [teacher_class_mappings_teacherId_idx] ON [dbo].[teacher_class_mappings]([teacherId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [teacher_class_mappings_grade_classId_idx] ON [dbo].[teacher_class_mappings]([grade], [classId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [knowledge_points_grade_idx] ON [dbo].[knowledge_points]([grade]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [knowledge_points_type_idx] ON [dbo].[knowledge_points]([type]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [knowledge_points_parentId_idx] ON [dbo].[knowledge_points]([parentId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_sourceId_sourceType_idx] ON [dbo].[interactions]([sourceId], [sourceType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_targetId_targetType_idx] ON [dbo].[interactions]([targetId], [targetType]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interactions_type_idx] ON [dbo].[interactions]([type]);

COMMIT TRAN;

END TRY
BEGIN CATCH

IF @@TRANCOUNT > 0
BEGIN
    ROLLBACK TRAN;
END;
THROW

END CATCH
