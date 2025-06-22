package com.example.orderapi.jms;

import com.example.orderapi.config.JmsConfig;
import com.example.orderapi.entity.Order;
import com.example.orderapi.service.OrderService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class OrderMessageListener {

    private static final Logger logger = LoggerFactory.getLogger(OrderMessageListener.class);

    @Autowired
    private OrderService orderService;

    @JmsListener(destination = JmsConfig.ORDER_PROCESSING_QUEUE)
    public void processOrder(Map<String, Object> message) {
        try {
            logger.info("Processing order message: {}", message);
            
            Long orderId = ((Number) message.get("orderId")).longValue();
            String status = (String) message.get("status");
            
            logger.info("Processing order {} with status {}", orderId, status);
            
            // Simulate order processing logic
            Order order = orderService.findById(orderId);
            
            if (order.getStatus() == Order.OrderStatus.PENDING) {
                // Auto-confirm orders after processing
                Thread.sleep(2000); // Simulate processing time
                orderService.confirmOrder(orderId);
                logger.info("Order {} automatically confirmed after processing", orderId);
            }
            
        } catch (Exception e) {
            logger.error("Error processing order message: {}", message, e);
            throw new RuntimeException("Failed to process order", e);
        }
    }

    @JmsListener(destination = JmsConfig.NOTIFICATION_QUEUE)
    public void handleNotification(Map<String, Object> notification) {
        try {
            logger.info("Handling notification: {}", notification);
            
            Long orderId = ((Number) notification.get("orderId")).longValue();
            Long userId = ((Number) notification.get("userId")).longValue();
            String userEmail = (String) notification.get("userEmail");
            String message = (String) notification.get("message");
            String status = (String) notification.get("status");
            
            // Simulate sending email notification
            logger.info("Sending email to {} for order {}: {}", userEmail, orderId, message);
            
            // Here you would integrate with an email service
            // For now, we just log the notification
            logger.info("Email notification sent successfully to {} for order {}", userEmail, orderId);
            
        } catch (Exception e) {
            logger.error("Error handling notification: {}", notification, e);
            throw new RuntimeException("Failed to handle notification", e);
        }
    }

    @JmsListener(destination = JmsConfig.INVENTORY_UPDATE_QUEUE)
    public void handleInventoryUpdate(Map<String, Object> update) {
        try {
            logger.info("Handling inventory update: {}", update);
            
            Long productId = ((Number) update.get("productId")).longValue();
            Integer newQuantity = ((Number) update.get("newQuantity")).intValue();
            String operation = (String) update.get("operation");
            
            logger.info("Inventory update for product {}: {} to quantity {}", productId, operation, newQuantity);
            
            // Here you could trigger additional business logic
            // such as reorder notifications, supplier alerts, etc.
            
            if (newQuantity < 10) {
                logger.warn("Low stock alert for product {}: only {} items remaining", productId, newQuantity);
                // Could send alert to procurement team
            }
            
            logger.info("Inventory update processed successfully for product {}", productId);
            
        } catch (Exception e) {
            logger.error("Error handling inventory update: {}", update, e);
            throw new RuntimeException("Failed to handle inventory update", e);
        }
    }
}
