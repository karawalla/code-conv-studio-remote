package com.example.demo.Util;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class FileUtils {
	
	public static void moveToArchive(File file, String archivePath) {
		try {
			File destDir = new File(archivePath);
			if(!destDir.exists()) destDir.mkdirs();
			
			Path target = new File(destDir, file.getName()).toPath();
			Files.move(file.toPath(), target, StandardCopyOption.REPLACE_EXISTING);
			
			System.out.println("📁 Moved file to archive: " + target.toString());
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	public static void copyToArchive(File file, String archivePath) {
		try {
			File archiveDir = new File(archivePath);
			if(!archiveDir.exists()) {
				archiveDir.mkdirs();
			}
			File destFile = new File(archiveDir, file.getName());
			Files.copy(file.toPath(), destFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
			System.out.println("Copied File to Archive: "+destFile.getAbsolutePath());
		}
		catch(IOException e) {
			e.printStackTrace();
		}
	}
	
	public static void markFileAsProcessed(File file) {
		String fileName = file.getName();
		String parentPath = file.getParent();
		
		String newName;
		if(fileName.contains("_processed")) {
			newName = fileName; //already renamed
		}else {
			int dotIndex = fileName.lastIndexOf('.');
			newName = dotIndex != -1
					? fileName.substring(0, dotIndex)+"_processed"+fileName.substring(dotIndex)
					: fileName + "_processed";
		}
		File renamedFile = new File(parentPath, newName);
		boolean success = file.renameTo(renamedFile);
		
		if(success) {
			System.out.println("Renames file as: "+renamedFile.getAbsolutePath());
		}else {
			System.out.println("Failed to rename file: "+file.getAbsolutePath());
		}
	}
}
