package com.example.orderapi.dto.request;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;

import java.util.List;

public class CreateOrderRequest {
    
    @NotEmpty(message = "Order items cannot be empty")
    @Valid
    private List<OrderItemRequest> items;
    
    @NotBlank(message = "Shipping address is required")
    @Size(max = 500, message = "Shipping address must not exceed 500 characters")
    private String shippingAddress;
    
    // Constructors
    public CreateOrderRequest() {}
    
    public CreateOrderRequest(List<OrderItemRequest> items, String shippingAddress) {
        this.items = items;
        this.shippingAddress = shippingAddress;
    }
    
    // Getters and Setters
    public List<OrderItemRequest> getItems() { return items; }
    public void setItems(List<OrderItemRequest> items) { this.items = items; }
    
    public String getShippingAddress() { return shippingAddress; }
    public void setShippingAddress(String shippingAddress) { this.shippingAddress = shippingAddress; }
    
    // Inner class for order items
    public static class OrderItemRequest {
        
        @jakarta.validation.constraints.NotNull(message = "Product ID is required")
        private Long productId;
        
        @jakarta.validation.constraints.NotNull(message = "Quantity is required")
        @jakarta.validation.constraints.Min(value = 1, message = "Quantity must be at least 1")
        private Integer quantity;
        
        // Constructors
        public OrderItemRequest() {}
        
        public OrderItemRequest(Long productId, Integer quantity) {
            this.productId = productId;
            this.quantity = quantity;
        }
        
        // Getters and Setters
        public Long getProductId() { return productId; }
        public void setProductId(Long productId) { this.productId = productId; }
        
        public Integer getQuantity() { return quantity; }
        public void setQuantity(Integer quantity) { this.quantity = quantity; }
    }
}
