package com.example.demo.Service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demo.Messaging.JmsProducer;

@Service
public class InvoiceFileService {
	
	@Autowired private JmsProducer jmsProducer;

	 public boolean process(File file) {
	        try (BufferedReader reader = new BufferedReader(new FileReader(file));
	             BufferedWriter writer = new BufferedWriter(new FileWriter("C:/Users/Pradeep/Desktop/Repo/Spring File Operation/SampleOutputFiles/processed_" + file.getName()))) {

	            String line;
	            while ((line = reader.readLine()) != null) {
	                writer.write(line + " - INVOICE PROCESSED");
	                writer.newLine();
	            }
	            
	            jmsProducer.sendStatusMessage(file.getName(), true ? "Processed Successfully" : "Processing Failed");
	            
	            return true;

	        } catch (IOException e) {
	            e.printStackTrace();
	            return false;
	        }
	    }
}
