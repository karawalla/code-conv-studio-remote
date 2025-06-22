package com.example.orderapi.repository;

import com.example.orderapi.entity.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    Optional<Product> findByName(String name);
    
    List<Product> findByCategory(String category);
    
    List<Product> findByBrand(String brand);
    
    Page<Product> findByActiveTrue(Pageable pageable);
    
    Page<Product> findByCategoryAndActiveTrue(String category, Pageable pageable);
    
    @Query("SELECT p FROM Product p WHERE p.active = true AND p.stockQuantity > 0")
    List<Product> findAvailableProducts();
    
    @Query("SELECT p FROM Product p WHERE p.price BETWEEN :minPrice AND :maxPrice AND p.active = true")
    List<Product> findByPriceRange(@Param("minPrice") BigDecimal minPrice, @Param("maxPrice") BigDecimal maxPrice);
    
    @Query("SELECT p FROM Product p WHERE p.name LIKE %:keyword% OR p.description LIKE %:keyword%")
    List<Product> searchByKeyword(@Param("keyword") String keyword);
    
    @Query("SELECT DISTINCT p.category FROM Product p WHERE p.active = true")
    List<String> findAllCategories();
    
    @Query("SELECT DISTINCT p.brand FROM Product p WHERE p.active = true")
    List<String> findAllBrands();
    
    @Query("SELECT p FROM Product p WHERE p.stockQuantity < :threshold")
    List<Product> findLowStockProducts(@Param("threshold") Integer threshold);
}
