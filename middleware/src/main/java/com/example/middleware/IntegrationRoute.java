package com.example.middleware;

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.component.snakeyaml.SnakeYAMLDataFormat;
import org.apache.camel.model.dataformat.JsonLibrary;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class IntegrationRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Route 1: Handle orders from shop
        from("kafka:orders")
            .log("Received message from Kafka: ${body}")
            .unmarshal().json(JsonLibrary.Jackson, Map.class)
            .choice()
                .when(simple("${body[country]} == 'Tunisia'"))
                    .marshal(new SnakeYAMLDataFormat())
                    .setHeader("Content-Type", constant("application/x-yaml"))
                    .to("http://aramex:3000/aramex")
                .otherwise()
                    .marshal().jacksonXml()
                    .setHeader("Content-Type", constant("application/xml"))
                    .to("http://dhl:80/dhl.php")
            .end();

        // Route 2: Handle status updates from Aramex
        from("jetty:http://0.0.0.0:8085/status-update")
            .log("Received status update from Aramex: ${body}")
            .to("kafka:order-status-updates");
    }
}
