/*
  Warnings:

  - You are about to alter the column `gradeName` on the `grades` table. The data in that column could be lost. The data in that column will be cast from `NVarChar(1000)` to `Int`.
  - You are about to drop the column `grade` on the `graph_nodes` table. All the data in the column will be lost.
  - You are about to drop the column `isActive` on the `graph_nodes` table. All the data in the column will be lost.
  - You are about to drop the column `school` on the `graph_nodes` table. All the data in the column will be lost.
  - You are about to drop the column `grade` on the `interaction_sessions` table. All the data in the column will be lost.
  - You are about to drop the column `meta` on the `interaction_sessions` table. All the data in the column will be lost.
  - You are about to drop the column `school` on the `interaction_sessions` table. All the data in the column will be lost.
  - You are about to drop the column `updatedAt` on the `interaction_sessions` table. All the data in the column will be lost.
  - You are about to drop the column `description` on the `learning_scenarios` table. All the data in the column will be lost.
  - You are about to alter the column `teachingGrade` on the `teacher_profiles` table. The data in that column could be lost. The data in that column will be cast from `NVarChar(1000)` to `Int`.
  - You are about to drop the `knowledge_relations` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `legacy_interactions` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `legacy_knowledge_points` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `legacy_students` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `legacy_teacher_class_mappings` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `legacy_teachers` table. If the table is not empty, all the data it contains will be lost.
  - Made the column `categoryName` on table `cognitive_dimension_defs` required. This step will fail if there are existing NULL values in that column.
  - Added the required column `scenarioId` to the `graph_nodes` table without a default value. This is not possible if the table is not empty.
  - Added the required column `gradeId` to the `interaction_sessions` table without a default value. This is not possible if the table is not empty.
  - Added the required column `schoolId` to the `interaction_sessions` table without a default value. This is not possible if the table is not empty.
  - Made the column `scoreLevel` on table `student_cognitive_dimension_scores` required. This step will fail if there are existing NULL values in that column.

*/
BEGIN TRY

BEGIN TRAN;

-- DropForeignKey
ALTER TABLE [dbo].[knowledge_profiles] DROP CONSTRAINT [knowledge_profiles_parentNodeId_fkey];

-- DropForeignKey
ALTER TABLE [dbo].[knowledge_relations] DROP CONSTRAINT [knowledge_relations_fromKnowledgeNodeId_fkey];

-- DropForeignKey
ALTER TABLE [dbo].[knowledge_relations] DROP CONSTRAINT [knowledge_relations_toKnowledgeNodeId_fkey];

-- DropIndex
ALTER TABLE [dbo].[grades] DROP CONSTRAINT [grades_schoolId_gradeName_key];

-- DropIndex
DROP INDEX [graph_nodes_nodeType_school_grade_idx] ON [dbo].[graph_nodes];

-- DropIndex
DROP INDEX [graph_nodes_school_grade_classId_idx] ON [dbo].[graph_nodes];

-- DropIndex
DROP INDEX [interaction_sessions_school_grade_classId_occurredAt_idx] ON [dbo].[interaction_sessions];

-- DropIndex
DROP INDEX [interactions_targetNodeId_idx] ON [dbo].[interactions];

-- DropIndex
DROP INDEX [learning_scenarios_isActive_sortOrder_idx] ON [dbo].[learning_scenarios];

-- AlterTable
ALTER TABLE [dbo].[cognitive_dimension_defs] ALTER COLUMN [categoryName] NVARCHAR(1000) NOT NULL;

-- AlterTable
ALTER TABLE [dbo].[grades] ALTER COLUMN [gradeName] INT NOT NULL;

-- AlterTable
ALTER TABLE [dbo].[graph_nodes] DROP CONSTRAINT [graph_nodes_isActive_df];
ALTER TABLE [dbo].[graph_nodes] DROP COLUMN [grade],
[isActive],
[school];
ALTER TABLE [dbo].[graph_nodes] ADD [gradeId] NVARCHAR(1000),
[scenarioId] NVARCHAR(1000) NOT NULL,
[schoolId] NVARCHAR(1000);

-- AlterTable
ALTER TABLE [dbo].[interaction_sessions] ALTER COLUMN [sessionName] NVARCHAR(1000) NULL;
ALTER TABLE [dbo].[interaction_sessions] DROP COLUMN [grade],
[meta],
[school],
[updatedAt];
ALTER TABLE [dbo].[interaction_sessions] ADD [gradeId] NVARCHAR(1000) NOT NULL,
[schoolId] NVARCHAR(1000) NOT NULL;

-- AlterTable
ALTER TABLE [dbo].[interactions] ALTER COLUMN [strength] DECIMAL(10,4) NOT NULL;

-- AlterTable
ALTER TABLE [dbo].[knowledge_profiles] ALTER COLUMN [content] NVARCHAR(1000) NULL;
ALTER TABLE [dbo].[knowledge_profiles] ALTER COLUMN [knowledgeType] NVARCHAR(1000) NULL;

-- AlterTable
ALTER TABLE [dbo].[learning_scenarios] DROP COLUMN [description];

-- AlterTable
ALTER TABLE [dbo].[student_cognitive_dimension_scores] ALTER COLUMN [scoreValue] DECIMAL(10,4) NOT NULL;
ALTER TABLE [dbo].[student_cognitive_dimension_scores] ALTER COLUMN [scoreLevel] NVARCHAR(1000) NOT NULL;

-- AlterTable
ALTER TABLE [dbo].[student_cognitive_profiles] ALTER COLUMN [totalScore] DECIMAL(10,4) NOT NULL;

-- AlterTable
ALTER TABLE [dbo].[teacher_profiles] ALTER COLUMN [teachingGrade] INT NULL;

-- DropTable
DROP TABLE [dbo].[knowledge_relations];

-- DropTable
DROP TABLE [dbo].[legacy_interactions];

-- DropTable
DROP TABLE [dbo].[legacy_knowledge_points];

-- DropTable
DROP TABLE [dbo].[legacy_students];

-- DropTable
DROP TABLE [dbo].[legacy_teacher_class_mappings];

-- DropTable
DROP TABLE [dbo].[legacy_teachers];

-- CreateIndex
ALTER TABLE [dbo].[grades] ADD CONSTRAINT [grades_schoolId_gradeName_key] UNIQUE NONCLUSTERED ([schoolId], [gradeName]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [graph_nodes_scenarioId_idx] ON [dbo].[graph_nodes]([scenarioId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [graph_nodes_schoolId_gradeId_classId_idx] ON [dbo].[graph_nodes]([schoolId], [gradeId], [classId]);

-- CreateIndex
CREATE NONCLUSTERED INDEX [interaction_sessions_schoolId_gradeId_classId_occurredAt_idx] ON [dbo].[interaction_sessions]([schoolId], [gradeId], [classId], [occurredAt]);

-- AddForeignKey
ALTER TABLE [dbo].[graph_nodes] ADD CONSTRAINT [graph_nodes_scenarioId_fkey] FOREIGN KEY ([scenarioId]) REFERENCES [dbo].[learning_scenarios]([id]) ON DELETE NO ACTION ON UPDATE CASCADE;

COMMIT TRAN;

END TRY
BEGIN CATCH

IF @@TRANCOUNT > 0
BEGIN
    ROLLBACK TRAN;
END;
THROW

END CATCH
