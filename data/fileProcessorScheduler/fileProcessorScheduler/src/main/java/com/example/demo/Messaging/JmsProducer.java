package com.example.demo.Messaging;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.stereotype.Component;

@Component
public class JmsProducer {
	
	@Autowired
	private JmsTemplate jmsTemplate;
	
	@Value("${jms.queue.name}")
	private String queue;
	
	public void sendStatusMessage(String fileName, String status) {
		String message = "File: "+fileName+", Status: "+status;
		jmsTemplate.convertAndSend(queue, message);
		System.out.println("📨 Sent JMS message: " + message);
	}
}
