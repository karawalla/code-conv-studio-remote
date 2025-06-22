package com.example.demo.Service;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demo.Model.OrderEntity;

import com.example.demo.Repository.OrderRepository;

@Service
public class OrderFileService {
	
	@Autowired
	private OrderRepository orderRepo;
	
	@Autowired
	private ModelMapper modelMapper;
	
//	@Autowired
//	private OrderEntity orderEnt;
	
	public boolean process(File file) {
		try(BufferedReader reader = new BufferedReader(new FileReader(file));
				BufferedWriter writer = new BufferedWriter(new FileWriter("C:/Users/Pradeep/Desktop/Repo/Spring File Operation/SampleOutputFiles/processed_"+file.getName()))
				){
			String line;
			while((line = reader.readLine()) != null) {
				writer.write(line+" - ORDER PROCESSED");
				writer.newLine();
			}
			
			
			
			OrderEntity order = new OrderEntity();
			
			order.setFileName(file.getName());
			
			orderRepo.save(order);
			
			if(order.getId() != null) {
				
				return true;
			}else {
				return false;
			}
		} catch(IOException e) {
			e.printStackTrace();
			return false;
		}
		
		
	}
}
