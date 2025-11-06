package com.widget.schedule;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.stage.Stage;

import java.net.URL;
import java.util.ResourceBundle;

public class LoginController implements Initializable {
    @FXML private TextField tokenField;
    @FXML private Label errorLabel;
    @FXML private Button loginButton;
    private static final String CORRECT_TOKEN = "mySecretToken123";

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        // Добавляем обработку Enter
        tokenField.setOnAction(e -> handleLogin());
    }

    @FXML
    private void handleLogin() {
        String enteredToken = tokenField.getText().trim();
        if (enteredToken.isEmpty()) {
            showError("Пожалуйста, введите токен");
            return;
        }
        if (enteredToken.equals(CORRECT_TOKEN)) {
            try {
                openScheduleWidget();
            } catch (Exception e) {
                showError("Ошибка загрузки главного окна");
            }
        } else {
            showError("Неверный токен. Попробуйте снова.");
            tokenField.clear();
        }
    }

    private void showError(String message) {
        errorLabel.setText(message);
        errorLabel.setVisible(true);
    }

    private void openScheduleWidget() throws Exception {
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/widget.fxml"));
        Parent root = loader.load();
        Scene scene = new Scene(root);
        scene.setFill(javafx.scene.paint.Color.TRANSPARENT);
        scene.getStylesheets().add(getClass().getResource("/css/styles.css").toExternalForm());

        Stage stage = (Stage) loginButton.getScene().getWindow();
        stage.setScene(scene);
        stage.setTitle("Schedule Widget");

        // Делаем окно draggable:
        root.setOnMousePressed(event -> {
            stage.setUserData(new double[]{event.getSceneX(), event.getSceneY()});
        });
        root.setOnMouseDragged(event -> {
            double[] offset = (double[]) stage.getUserData();
            stage.setX(event.getScreenX() - offset[0]);
            stage.setY(event.getScreenY() - offset[1]);
        });
    }
}
