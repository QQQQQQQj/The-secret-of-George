package org.web;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

import javax.sql.DataSource;

@SpringBootApplication
public class MainApplication {

	public static void main(String[] args) {

		SpringApplication.run(MainApplication.class, args);

	}

	@Bean
	public JdbcTemplate jdbcTemplate(DataSource dataSource) {
		return new JdbcTemplate(dataSource);
	}

	@Bean
	public DataSource mysqlDataSource() {
		final DriverManagerDataSource dataSource = new DriverManagerDataSource();
		dataSource.setDriverClassName("com.mysql.jdbc.Driver");
		dataSource.setUrl("jdbc:mysql://127.0.0.1:3306/shangpinfenxistr?serverTimezone=UTC");
		dataSource.setUsername("root");
		dataSource.setPassword("root");

		return dataSource;
	}
}
