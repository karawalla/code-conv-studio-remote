package com.example.demo.Service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class InventoryFileService {
	
	public boolean process(File file) {
		
        try (BufferedReader reader = new BufferedReader(new FileReader(file));
             BufferedWriter writer = new BufferedWriter(new FileWriter("C:/Users/Pradeep/Desktop/Repo/Spring File Operation/SampleOutputFiles/processed_" + file.getName()))) {

            String line;
            while ((line = reader.readLine()) != null) {
                writer.write(line + " - INVENTORY PROCESSED");
                writer.newLine();
            }
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.TEXT_PLAIN);
            
            HttpEntity<String> entity = new HttpEntity<>(file.getName(), headers);
            
            RestTemplate restTemplate = new RestTemplate();
            
        	Boolean result = restTemplate.postForObject("http://localhost:8087/api/inventories/inventory", entity, Boolean.class);

            return result;

        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
}
