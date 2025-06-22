package com.example.orderapi.dto.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public class OrderResponse {
    
    private Long id;
    private String status;
    private BigDecimal totalAmount;
    private String shippingAddress;
    private LocalDateTime orderDate;
    private LocalDateTime shippedDate;
    private LocalDateTime deliveredDate;
    private UserSummary user;
    private List<OrderItemResponse> items;
    
    // Constructors
    public OrderResponse() {}
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    
    public String getShippingAddress() { return shippingAddress; }
    public void setShippingAddress(String shippingAddress) { this.shippingAddress = shippingAddress; }
    
    public LocalDateTime getOrderDate() { return orderDate; }
    public void setOrderDate(LocalDateTime orderDate) { this.orderDate = orderDate; }
    
    public LocalDateTime getShippedDate() { return shippedDate; }
    public void setShippedDate(LocalDateTime shippedDate) { this.shippedDate = shippedDate; }
    
    public LocalDateTime getDeliveredDate() { return deliveredDate; }
    public void setDeliveredDate(LocalDateTime deliveredDate) { this.deliveredDate = deliveredDate; }
    
    public UserSummary getUser() { return user; }
    public void setUser(UserSummary user) { this.user = user; }
    
    public List<OrderItemResponse> getItems() { return items; }
    public void setItems(List<OrderItemResponse> items) { this.items = items; }
    
    // Inner classes
    public static class UserSummary {
        private Long id;
        private String username;
        private String firstName;
        private String lastName;
        
        public UserSummary() {}
        
        public UserSummary(Long id, String username, String firstName, String lastName) {
            this.id = id;
            this.username = username;
            this.firstName = firstName;
            this.lastName = lastName;
        }
        
        // Getters and Setters
        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        
        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
        
        public String getFirstName() { return firstName; }
        public void setFirstName(String firstName) { this.firstName = firstName; }
        
        public String getLastName() { return lastName; }
        public void setLastName(String lastName) { this.lastName = lastName; }
    }
    
    public static class OrderItemResponse {
        private Long id;
        private ProductSummary product;
        private Integer quantity;
        private BigDecimal unitPrice;
        private BigDecimal totalPrice;
        
        public OrderItemResponse() {}
        
        // Getters and Setters
        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        
        public ProductSummary getProduct() { return product; }
        public void setProduct(ProductSummary product) { this.product = product; }
        
        public Integer getQuantity() { return quantity; }
        public void setQuantity(Integer quantity) { this.quantity = quantity; }
        
        public BigDecimal getUnitPrice() { return unitPrice; }
        public void setUnitPrice(BigDecimal unitPrice) { this.unitPrice = unitPrice; }
        
        public BigDecimal getTotalPrice() { return totalPrice; }
        public void setTotalPrice(BigDecimal totalPrice) { this.totalPrice = totalPrice; }
    }
    
    public static class ProductSummary {
        private Long id;
        private String name;
        private String category;
        private String brand;
        
        public ProductSummary() {}
        
        public ProductSummary(Long id, String name, String category, String brand) {
            this.id = id;
            this.name = name;
            this.category = category;
            this.brand = brand;
        }
        
        // Getters and Setters
        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        
        public String getBrand() { return brand; }
        public void setBrand(String brand) { this.brand = brand; }
    }
}
