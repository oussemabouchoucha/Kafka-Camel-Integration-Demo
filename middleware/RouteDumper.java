package com.example.middleware;

import org.apache.camel.CamelContext;
import org.apache.camel.model.ModelCamelContext;
import org.apache.camel.model.RouteDefinition;
import org.apache.camel.model.RoutesDefinition;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import java.util.List;

@Component
public class RouteDumper implements CommandLineRunner {

    private final CamelContext camelContext;

    public RouteDumper(CamelContext camelContext) {
        this.camelContext = camelContext;
    }

    @Override
    public void run(String... args) throws Exception {
        System.out.println("============== ROUTE XML DUMP START ==============");
        try {
            ModelCamelContext mcc = camelContext.adapt(ModelCamelContext.class);
            List<RouteDefinition> routes = mcc.getRouteDefinitions();
            String xml = mcc.getModelToXMLDumper().dumpModelAsXml(camelContext, new RoutesDefinition(routes));
            System.out.println(xml);
        } catch (Exception e) {
            System.err.println("ERREUR DUMP XML: " + e.getMessage());
            e.printStackTrace();
        }
        System.out.println("============== ROUTE XML DUMP END ==============");
    }
}