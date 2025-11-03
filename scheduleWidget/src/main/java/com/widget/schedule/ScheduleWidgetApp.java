package com.widget.schedule;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

import java.util.Objects;

public class ScheduleWidgetApp extends Application {

    private double xOffset = 0;
    private double yOffset = 0;

    @Override
    public void start(Stage primaryStage) throws Exception {
        FXMLLoader loader = new FXMLLoader(Objects.requireNonNull(getClass().getResource("/fxml/widget.fxml")));
        Pane root = loader.load();

        Image icon = new Image(getClass().getResourceAsStream("/icons/scheduleWidget.jpg"));
        primaryStage.getIcons().add(icon);

        // Create scene with transparent background
        Scene scene = new Scene(root);
        scene.setFill(Color.TRANSPARENT);

        // Apply CSS styles
        scene.getStylesheets().add(Objects.requireNonNull(getClass().getResource("/css/styles.css")).toExternalForm());

        // Configure stage
        primaryStage.initStyle(StageStyle.TRANSPARENT);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Schedule Widget");
        primaryStage.setAlwaysOnTop(true);
        primaryStage.setResizable(false);

        // Make window draggable
        scene.setOnMousePressed(event -> {
            xOffset = event.getSceneX();
            yOffset = event.getSceneY();
        });

        scene.setOnMouseDragged(event -> {
            primaryStage.setX(event.getScreenX() - xOffset);
            primaryStage.setY(event.getScreenY() - yOffset);
        });

        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}