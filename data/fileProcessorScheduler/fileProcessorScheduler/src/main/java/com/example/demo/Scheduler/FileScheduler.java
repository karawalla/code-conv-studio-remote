package com.example.demo.Scheduler;

import java.io.File;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.example.demo.Service.FileProcessingService;

@Component
public class FileScheduler {
	
	@Autowired
	private FileProcessingService fileProcessingService;
	
	@Scheduled(fixedRate = 60000) //Every 60 seconds
	public void pollDirectory() {
		File folder = new File("C:\\Users\\Pradeep\\Desktop\\Repo\\Spring File Operation\\SampleFiles\\");
		File[] files = folder.listFiles();
		
		if(files != null) {
			for(File file : files) {
				fileProcessingService.routeFile(file);
			}
		}
	}
}
