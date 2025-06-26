package com.example.demo.Controller;

import java.io.File;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.Service.FileProcessingService;

@RestController
@RequestMapping("/api/files")
public class FileProcessorController {
	
	@Autowired
	private FileProcessingService fileProcessingService;
	
	@PostMapping("/process")
	public ResponseEntity<String> processFile(@RequestParam String filePath){
		System.out.println("FilePath : "+filePath);
		File file = new File(filePath);
		System.out.println("File : "+file);
		
		if (!file.exists()) return ResponseEntity.badRequest().body("File not found");
		
		boolean status = fileProcessingService.routeFile(file);
		return ResponseEntity.ok("File processed: " + (status ? "Success" : "Failure"));
	}
}
