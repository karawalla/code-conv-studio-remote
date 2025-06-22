package com.example.orderapi.repository;

import com.example.orderapi.entity.Order;
import com.example.orderapi.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    List<Order> findByUser(User user);
    
    Page<Order> findByUser(User user, Pageable pageable);
    
    List<Order> findByStatus(Order.OrderStatus status);
    
    Page<Order> findByStatus(Order.OrderStatus status, Pageable pageable);
    
    @Query("SELECT o FROM Order o WHERE o.user.id = :userId")
    List<Order> findByUserId(@Param("userId") Long userId);
    
    @Query("SELECT o FROM Order o WHERE o.orderDate BETWEEN :startDate AND :endDate")
    List<Order> findOrdersBetweenDates(@Param("startDate") LocalDateTime startDate, 
                                       @Param("endDate") LocalDateTime endDate);
    
    @Query("SELECT o FROM Order o WHERE o.totalAmount >= :minAmount")
    List<Order> findOrdersAboveAmount(@Param("minAmount") BigDecimal minAmount);
    
    @Query("SELECT COUNT(o) FROM Order o WHERE o.status = :status")
    long countByStatus(@Param("status") Order.OrderStatus status);
    
    @Query("SELECT SUM(o.totalAmount) FROM Order o WHERE o.status = 'DELIVERED' AND o.deliveredDate BETWEEN :startDate AND :endDate")
    BigDecimal getTotalRevenueForPeriod(@Param("startDate") LocalDateTime startDate, 
                                        @Param("endDate") LocalDateTime endDate);
    
    @Query("SELECT o FROM Order o JOIN FETCH o.orderItems oi JOIN FETCH oi.product WHERE o.id = :orderId")
    Order findOrderWithItems(@Param("orderId") Long orderId);
    
    @Query("SELECT o FROM Order o WHERE o.user = :user ORDER BY o.orderDate DESC")
    List<Order> findRecentOrdersByUser(@Param("user") User user, Pageable pageable);
}
