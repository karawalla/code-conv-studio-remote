package com.example.orderapi.controller;

import com.example.orderapi.dto.request.CreateOrderRequest;
import com.example.orderapi.dto.response.OrderResponse;
import com.example.orderapi.entity.Order;
import com.example.orderapi.entity.User;
import com.example.orderapi.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/orders")
@SecurityRequirement(name = "bearerAuth")
@Tag(name = "Orders", description = "Order management APIs")
public class OrderController {

    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);

    @Autowired
    private OrderService orderService;

    @GetMapping
    @Operation(summary = "Get user orders", description = "Retrieve paginated orders for the authenticated user")
    public ResponseEntity<Page<OrderResponse>> getUserOrders(
            Authentication authentication,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        User user = (User) authentication.getPrincipal();
        Pageable pageable = PageRequest.of(page, size, Sort.by("orderDate").descending());
        Page<Order> orders = orderService.findOrdersByUser(user, pageable);
        
        Page<OrderResponse> orderResponses = orders.map(this::convertToOrderResponse);
        return ResponseEntity.ok(orderResponses);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get order by ID", description = "Retrieve a specific order by ID")
    public ResponseEntity<OrderResponse> getOrderById(@PathVariable Long id, Authentication authentication) {
        logger.info("Fetching order with id: {}", id);
        
        Order order = orderService.findOrderWithItems(id);
        User user = (User) authentication.getPrincipal();
        
        // Check if user owns the order or is admin
        if (!order.getUser().getId().equals(user.getId()) && !user.getRole().equals(User.Role.ADMIN)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        OrderResponse response = convertToOrderResponse(order);
        return ResponseEntity.ok(response);
    }

    @PostMapping
    @Operation(summary = "Create order", description = "Create a new order for the authenticated user")
    public ResponseEntity<OrderResponse> createOrder(
            @Valid @RequestBody CreateOrderRequest request,
            Authentication authentication) {
        
        User user = (User) authentication.getPrincipal();
        logger.info("Creating order for user: {}", user.getUsername());
        
        Order order = orderService.createOrder(user, request);
        OrderResponse response = convertToOrderResponse(order);
        
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @PutMapping("/{id}/confirm")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Confirm order", description = "Confirm a pending order (Admin only)")
    public ResponseEntity<OrderResponse> confirmOrder(@PathVariable Long id) {
        logger.info("Confirming order with id: {}", id);
        Order order = orderService.confirmOrder(id);
        OrderResponse response = convertToOrderResponse(order);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}/ship")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Ship order", description = "Mark order as shipped (Admin only)")
    public ResponseEntity<OrderResponse> shipOrder(@PathVariable Long id) {
        logger.info("Shipping order with id: {}", id);
        Order order = orderService.shipOrder(id);
        OrderResponse response = convertToOrderResponse(order);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}/deliver")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Deliver order", description = "Mark order as delivered (Admin only)")
    public ResponseEntity<OrderResponse> deliverOrder(@PathVariable Long id) {
        logger.info("Delivering order with id: {}", id);
        Order order = orderService.deliverOrder(id);
        OrderResponse response = convertToOrderResponse(order);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{id}/cancel")
    @Operation(summary = "Cancel order", description = "Cancel an order (User can cancel own orders, Admin can cancel any)")
    public ResponseEntity<OrderResponse> cancelOrder(@PathVariable Long id, Authentication authentication) {
        logger.info("Cancelling order with id: {}", id);
        
        Order order = orderService.findById(id);
        User user = (User) authentication.getPrincipal();
        
        // Check if user owns the order or is admin
        if (!order.getUser().getId().equals(user.getId()) && !user.getRole().equals(User.Role.ADMIN)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        
        Order cancelledOrder = orderService.cancelOrder(id);
        OrderResponse response = convertToOrderResponse(cancelledOrder);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/status/{status}")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Get orders by status", description = "Retrieve orders by status (Admin only)")
    public ResponseEntity<Page<OrderResponse>> getOrdersByStatus(
            @PathVariable String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        Order.OrderStatus orderStatus = Order.OrderStatus.valueOf(status.toUpperCase());
        Pageable pageable = PageRequest.of(page, size, Sort.by("orderDate").descending());
        Page<Order> orders = orderService.findOrdersByStatus(orderStatus, pageable);
        
        Page<OrderResponse> orderResponses = orders.map(this::convertToOrderResponse);
        return ResponseEntity.ok(orderResponses);
    }

    @GetMapping("/date-range")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Get orders by date range", description = "Retrieve orders within date range (Admin only)")
    public ResponseEntity<List<OrderResponse>> getOrdersByDateRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<Order> orders = orderService.findOrdersBetweenDates(startDate, endDate);
        List<OrderResponse> orderResponses = orders.stream()
                .map(this::convertToOrderResponse)
                .collect(Collectors.toList());
        
        return ResponseEntity.ok(orderResponses);
    }

    @GetMapping("/revenue")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Get revenue for period", description = "Get total revenue for specified period (Admin only)")
    public ResponseEntity<BigDecimal> getRevenueForPeriod(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        BigDecimal revenue = orderService.getTotalRevenueForPeriod(startDate, endDate);
        return ResponseEntity.ok(revenue);
    }

    @GetMapping("/stats/status-count")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Get order count by status", description = "Get count of orders by status (Admin only)")
    public ResponseEntity<Long> getOrderCountByStatus(@RequestParam String status) {
        Order.OrderStatus orderStatus = Order.OrderStatus.valueOf(status.toUpperCase());
        long count = orderService.getOrderCountByStatus(orderStatus);
        return ResponseEntity.ok(count);
    }

    private OrderResponse convertToOrderResponse(Order order) {
        OrderResponse response = new OrderResponse();
        response.setId(order.getId());
        response.setStatus(order.getStatus().toString());
        response.setTotalAmount(order.getTotalAmount());
        response.setShippingAddress(order.getShippingAddress());
        response.setOrderDate(order.getOrderDate());
        response.setShippedDate(order.getShippedDate());
        response.setDeliveredDate(order.getDeliveredDate());
        
        // Set user summary
        OrderResponse.UserSummary userSummary = new OrderResponse.UserSummary(
            order.getUser().getId(),
            order.getUser().getUsername(),
            order.getUser().getFirstName(),
            order.getUser().getLastName()
        );
        response.setUser(userSummary);
        
        // Set order items
        if (order.getOrderItems() != null) {
            List<OrderResponse.OrderItemResponse> items = order.getOrderItems().stream()
                .map(item -> {
                    OrderResponse.OrderItemResponse itemResponse = new OrderResponse.OrderItemResponse();
                    itemResponse.setId(item.getId());
                    itemResponse.setQuantity(item.getQuantity());
                    itemResponse.setUnitPrice(item.getUnitPrice());
                    itemResponse.setTotalPrice(item.getTotalPrice());
                    
                    OrderResponse.ProductSummary productSummary = new OrderResponse.ProductSummary(
                        item.getProduct().getId(),
                        item.getProduct().getName(),
                        item.getProduct().getCategory(),
                        item.getProduct().getBrand()
                    );
                    itemResponse.setProduct(productSummary);
                    
                    return itemResponse;
                })
                .collect(Collectors.toList());
            response.setItems(items);
        }
        
        return response;
    }
}
