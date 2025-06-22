package com.example.demo.Controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/inventories")
public class InventoryController {
	
	@PostMapping("/inventory")
	public ResponseEntity<Boolean> postInventory(@RequestBody String fileName){
		System.out.println("Inventory Files Processed : "+fileName);
		return ResponseEntity.ok(true);
	}
}
