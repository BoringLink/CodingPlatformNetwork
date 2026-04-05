/*
  Warnings:

  - You are about to drop the column `categoryName` on the `cognitive_dimension_defs` table. All the data in the column will be lost.
  - Added the required column `category` to the `cognitive_dimension_defs` table without a default value. This is not possible if the table is not empty.

*/
BEGIN TRY

BEGIN TRAN;

-- AlterTable
ALTER TABLE [dbo].[cognitive_dimension_defs] DROP COLUMN [categoryName];
ALTER TABLE [dbo].[cognitive_dimension_defs] ADD [category] NVARCHAR(1000) NOT NULL;

COMMIT TRAN;

END TRY
BEGIN CATCH

IF @@TRANCOUNT > 0
BEGIN
    ROLLBACK TRAN;
END;
THROW

END CATCH
