package com.example.orderapi.service;

import com.example.orderapi.dto.request.CreateOrderRequest;
import com.example.orderapi.entity.Order;
import com.example.orderapi.entity.OrderItem;
import com.example.orderapi.entity.Product;
import com.example.orderapi.entity.User;
import com.example.orderapi.exception.ResourceNotFoundException;
import com.example.orderapi.repository.OrderRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
@Transactional
public class OrderService {

    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ProductService productService;

    @Autowired
    private JmsService jmsService;

    @Transactional(readOnly = true)
    public Order findById(Long id) {
        return orderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Order not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public Order findOrderWithItems(Long id) {
        Order order = orderRepository.findOrderWithItems(id);
        if (order == null) {
            throw new ResourceNotFoundException("Order not found with id: " + id);
        }
        return order;
    }

    @Transactional(readOnly = true)
    public List<Order> findOrdersByUser(User user) {
        return orderRepository.findByUser(user);
    }

    @Transactional(readOnly = true)
    public Page<Order> findOrdersByUser(User user, Pageable pageable) {
        return orderRepository.findByUser(user, pageable);
    }

    @Transactional(readOnly = true)
    public List<Order> findOrdersByStatus(Order.OrderStatus status) {
        return orderRepository.findByStatus(status);
    }

    @Transactional(readOnly = true)
    public Page<Order> findOrdersByStatus(Order.OrderStatus status, Pageable pageable) {
        return orderRepository.findByStatus(status, pageable);
    }

    public Order createOrder(User user, CreateOrderRequest request) {
        logger.info("Creating order for user: {}", user.getUsername());

        // Validate and calculate order
        Set<OrderItem> orderItems = new HashSet<>();
        BigDecimal totalAmount = BigDecimal.ZERO;

        for (CreateOrderRequest.OrderItemRequest itemRequest : request.getItems()) {
            Product product = productService.findById(itemRequest.getProductId());
            
            // Check stock availability
            if (product.getStockQuantity() < itemRequest.getQuantity()) {
                throw new IllegalArgumentException("Insufficient stock for product: " + product.getName() + 
                    ". Available: " + product.getStockQuantity() + ", Requested: " + itemRequest.getQuantity());
            }

            OrderItem orderItem = new OrderItem();
            orderItem.setProduct(product);
            orderItem.setQuantity(itemRequest.getQuantity());
            orderItem.setUnitPrice(product.getPrice());
            
            orderItems.add(orderItem);
            totalAmount = totalAmount.add(product.getPrice().multiply(BigDecimal.valueOf(itemRequest.getQuantity())));
        }

        // Create order
        Order order = new Order(user, totalAmount, request.getShippingAddress());
        Order savedOrder = orderRepository.save(order);

        // Set order reference in order items and save
        for (OrderItem item : orderItems) {
            item.setOrder(savedOrder);
        }
        savedOrder.setOrderItems(orderItems);
        savedOrder = orderRepository.save(savedOrder);

        // Reduce stock for each product
        for (OrderItem item : orderItems) {
            productService.reduceStock(item.getProduct().getId(), item.getQuantity());
        }

        // Send order to processing queue
        jmsService.sendOrderForProcessing(savedOrder);

        logger.info("Order created successfully with id: {}", savedOrder.getId());
        return savedOrder;
    }

    public Order confirmOrder(Long orderId) {
        logger.info("Confirming order with id: {}", orderId);
        Order order = findById(orderId);
        
        if (order.getStatus() != Order.OrderStatus.PENDING) {
            throw new IllegalStateException("Order cannot be confirmed. Current status: " + order.getStatus());
        }
        
        order.confirm();
        Order confirmedOrder = orderRepository.save(order);
        
        // Send notification
        jmsService.sendOrderNotification(confirmedOrder, "Order confirmed");
        
        logger.info("Order confirmed successfully: {}", orderId);
        return confirmedOrder;
    }

    public Order shipOrder(Long orderId) {
        logger.info("Shipping order with id: {}", orderId);
        Order order = findById(orderId);
        
        if (order.getStatus() != Order.OrderStatus.CONFIRMED && order.getStatus() != Order.OrderStatus.PROCESSING) {
            throw new IllegalStateException("Order cannot be shipped. Current status: " + order.getStatus());
        }
        
        order.ship();
        Order shippedOrder = orderRepository.save(order);
        
        // Send notification
        jmsService.sendOrderNotification(shippedOrder, "Order shipped");
        
        logger.info("Order shipped successfully: {}", orderId);
        return shippedOrder;
    }

    public Order deliverOrder(Long orderId) {
        logger.info("Delivering order with id: {}", orderId);
        Order order = findById(orderId);
        
        if (order.getStatus() != Order.OrderStatus.SHIPPED) {
            throw new IllegalStateException("Order cannot be delivered. Current status: " + order.getStatus());
        }
        
        order.deliver();
        Order deliveredOrder = orderRepository.save(order);
        
        // Send notification
        jmsService.sendOrderNotification(deliveredOrder, "Order delivered");
        
        logger.info("Order delivered successfully: {}", orderId);
        return deliveredOrder;
    }

    public Order cancelOrder(Long orderId) {
        logger.info("Cancelling order with id: {}", orderId);
        Order order = findOrderWithItems(orderId);
        
        if (order.getStatus() == Order.OrderStatus.SHIPPED || order.getStatus() == Order.OrderStatus.DELIVERED) {
            throw new IllegalStateException("Order cannot be cancelled. Current status: " + order.getStatus());
        }
        
        // Restore stock if order was confirmed or processing
        if (order.getStatus() == Order.OrderStatus.CONFIRMED || order.getStatus() == Order.OrderStatus.PROCESSING) {
            for (OrderItem item : order.getOrderItems()) {
                productService.increaseStock(item.getProduct().getId(), item.getQuantity());
            }
        }
        
        order.cancel();
        Order cancelledOrder = orderRepository.save(order);
        
        // Send notification
        jmsService.sendOrderNotification(cancelledOrder, "Order cancelled");
        
        logger.info("Order cancelled successfully: {}", orderId);
        return cancelledOrder;
    }

    @Transactional(readOnly = true)
    public List<Order> findOrdersBetweenDates(LocalDateTime startDate, LocalDateTime endDate) {
        return orderRepository.findOrdersBetweenDates(startDate, endDate);
    }

    @Transactional(readOnly = true)
    public BigDecimal getTotalRevenueForPeriod(LocalDateTime startDate, LocalDateTime endDate) {
        BigDecimal revenue = orderRepository.getTotalRevenueForPeriod(startDate, endDate);
        return revenue != null ? revenue : BigDecimal.ZERO;
    }

    @Transactional(readOnly = true)
    public long getOrderCountByStatus(Order.OrderStatus status) {
        return orderRepository.countByStatus(status);
    }
}
