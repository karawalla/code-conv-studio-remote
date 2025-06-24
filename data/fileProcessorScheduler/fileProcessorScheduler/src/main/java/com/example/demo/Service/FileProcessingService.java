package com.example.demo.Service;

import java.io.File;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demo.Messaging.JmsProducer;
import com.example.demo.Util.FileUtils;

@Service
public class FileProcessingService {
	
	@Autowired private OrderFileService orderService;
    @Autowired private InvoiceFileService invoiceService;
    @Autowired private InventoryFileService inventoryService;
    @Autowired private JmsProducer jmsProducer;

	public boolean routeFile(File file) {
		System.out.println("File : "+file);
		boolean result = false;
		try {
			String name = file.getName().toLowerCase();
			
			System.out.println("File Name: "+name);
					
			if(name.contains("order")) {
				result = orderService.process(file);
			} else if(name.contains("invoice")) {
				result = invoiceService.process(file);
			} else if(name.contains("inventory")) {
				result = inventoryService.process(file);
			}
			
			jmsProducer.sendStatusMessage(file.getName(), result ? "Processed Successfully" : "Processing Failed");
			
			//Move to archive folder
//			if(result) {
//				FileUtils.moveToArchive(file, "C:/Users/Pradeep/Desktop/Repo/Spring File Operation/Archive");
//			}
			
			//Copy to archive folder and change the name of source files.
			if (result) {
	            FileUtils.copyToArchive(file, "C:/Users/Pradeep/Desktop/Repo/Spring File Operation/Archive");
	            FileUtils.markFileAsProcessed(file);
	        }

			return result;
		}
		catch(Exception e) {
			e.printStackTrace();
			jmsProducer.sendStatusMessage(file.getName(), "Processing Exception: " + e.getMessage());
			return false;
		}
		
	}

}
