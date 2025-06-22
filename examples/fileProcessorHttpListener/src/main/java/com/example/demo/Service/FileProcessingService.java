package com.example.demo.Service;

import java.io.File;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demo.Messaging.JmsProducer;


@Service
public class FileProcessingService {
	
	@Autowired private OrderFileService orderService;
    @Autowired private InvoiceFileService invoiceService;
    @Autowired private InventoryFileService inventoryService;
    

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
			
			
			
			return result;
		}
		catch(Exception e) {
			e.printStackTrace();
			return false;
		}
		
	}

}
