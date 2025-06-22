package com.example.demo.Repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.Model.OrderEntity;

public interface OrderRepository extends JpaRepository<OrderEntity, Long>{

}
