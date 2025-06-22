package com.example.orderapi.service;

import com.example.orderapi.config.JmsConfig;
import com.example.orderapi.entity.Order;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class JmsService {

    private static final Logger logger = LoggerFactory.getLogger(JmsService.class);

    @Autowired
    private JmsTemplate jmsTemplate;

    public void sendOrderForProcessing(Order order) {
        logger.info("Sending order {} to processing queue", order.getId());
        
        Map<String, Object> message = new HashMap<>();
        message.put("orderId", order.getId());
        message.put("userId", order.getUser().getId());
        message.put("totalAmount", order.getTotalAmount());
        message.put("status", order.getStatus().toString());
        message.put("timestamp", System.currentTimeMillis());
        
        jmsTemplate.convertAndSend(JmsConfig.ORDER_PROCESSING_QUEUE, message);
        logger.info("Order {} sent to processing queue successfully", order.getId());
    }

    public void sendOrderNotification(Order order, String message) {
        logger.info("Sending notification for order {}: {}", order.getId(), message);
        
        Map<String, Object> notification = new HashMap<>();
        notification.put("orderId", order.getId());
        notification.put("userId", order.getUser().getId());
        notification.put("userEmail", order.getUser().getEmail());
        notification.put("message", message);
        notification.put("status", order.getStatus().toString());
        notification.put("timestamp", System.currentTimeMillis());
        
        jmsTemplate.convertAndSend(JmsConfig.NOTIFICATION_QUEUE, notification);
        logger.info("Notification sent for order {} successfully", order.getId());
    }

    public void sendInventoryUpdate(Long productId, Integer newQuantity, String operation) {
        logger.info("Sending inventory update for product {}: {} to {}", productId, operation, newQuantity);
        
        Map<String, Object> update = new HashMap<>();
        update.put("productId", productId);
        update.put("newQuantity", newQuantity);
        update.put("operation", operation); // REDUCE, INCREASE, UPDATE
        update.put("timestamp", System.currentTimeMillis());
        
        jmsTemplate.convertAndSend(JmsConfig.INVENTORY_UPDATE_QUEUE, update);
        logger.info("Inventory update sent for product {} successfully", productId);
    }

    public void sendMessage(String destination, Object message) {
        logger.info("Sending message to destination: {}", destination);
        jmsTemplate.convertAndSend(destination, message);
        logger.info("Message sent to {} successfully", destination);
    }
}
