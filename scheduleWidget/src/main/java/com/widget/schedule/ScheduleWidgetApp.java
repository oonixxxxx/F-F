package com.widget.schedule;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

public class ScheduleWidgetApp extends Application {
    @Override
    public void start(Stage primaryStage) throws Exception {
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/login.fxml"));
        Parent root = loader.load();

        Scene scene = new Scene(root);
        scene.setFill(javafx.scene.paint.Color.TRANSPARENT);
        scene.getStylesheets().add(getClass().getResource("/css/styles.css").toExternalForm());

        primaryStage.initStyle(StageStyle.TRANSPARENT);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Login");
        primaryStage.setResizable(false);
        primaryStage.show();

        // Делаем окно draggable
        root.setOnMousePressed(event -> {
            primaryStage.setUserData(new double[]{event.getSceneX(), event.getSceneY()});
        });
        root.setOnMouseDragged(event -> {
            double[] offset = (double[]) primaryStage.getUserData();
            primaryStage.setX(event.getScreenX() - offset[0]);
            primaryStage.setY(event.getScreenY() - offset[1]);
        });
    }

    public static void main(String[] args) { launch(args); }
}
