package com.widget.schedule;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.util.Duration;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class WidgetController {

    @FXML
    private VBox scheduleContainer;

    @FXML
    private Label headerTitle;

    @FXML
    private Label headerSubtitle;

    @FXML
    private Label headerTime;

    @FXML
    private ProgressBar progressBar;

    private List<ScheduleTask> tasks = new ArrayList<>();
    private Timeline timeline;

    @FXML
    public void initialize() {
        // Пример задач
        ObjectMapper mapper = new ObjectMapper();
        try {
            tasks = Arrays.asList(
                    mapper.readValue(new File("tasks.json"), ScheduleTask[].class)
            );
        } catch (IOException e) {
            e.printStackTrace();
        }

        refreshScheduleDisplay();
        updateCurrentTask();

        timeline = new Timeline(new KeyFrame(Duration.seconds(60), event -> {
            updateCurrentTask();
        }));
        timeline.setCycleCount(Timeline.INDEFINITE);
        timeline.play();

        // Дополнительное применение стиля для скругления
        progressBar.getStyleClass().add("task-progress-bar");
    }

    private void refreshScheduleDisplay() {
        scheduleContainer.getChildren().clear();
        for (ScheduleTask task : tasks) {
            HBox taskItem = new HBox(8);
            taskItem.getStyleClass().add("schedule-item");

            Label bullet = new Label("●");
            bullet.getStyleClass().add("bullet");

            VBox vbox = new VBox(1);
            Label timeLabel = new Label(task.getStartTime() + " - " + task.getEndTime());
            timeLabel.getStyleClass().add("schedule-time");

            vbox.getChildren().add(timeLabel);

            if (!task.getTitle().isEmpty()) {
                Label titleLabel = new Label(task.getTitle());
                titleLabel.getStyleClass().add("schedule-title");
                vbox.getChildren().add(titleLabel);
            }

            if (!task.getSubtitle().isEmpty()) {
                Label subtitleLabel = new Label(task.getSubtitle());
                subtitleLabel.getStyleClass().add("schedule-subtitle");
                vbox.getChildren().add(subtitleLabel);
            }

            taskItem.getChildren().addAll(bullet, vbox);
            scheduleContainer.getChildren().add(taskItem);
        }
    }

    private void updateCurrentTask() {
        LocalTime now = LocalTime.now();
        ScheduleTask currentTask = getCurrentTask(now);

        // Подсчет завершенных задач по времени
        int finishedTasksCount = 0;
        for (ScheduleTask task : tasks) {
            LocalTime end = LocalTime.parse(task.getEndTime(), DateTimeFormatter.ofPattern("HH:mm"));
            if (now.isAfter(end) || now.equals(end)) {
                finishedTasksCount++;
            }
        }

        double progress = (double) finishedTasksCount / tasks.size();
        if (progress > 1.0) progress = 1.0;
        progressBar.setProgress(progress);


        // Отображение задачи/завершения
        if (finishedTasksCount == tasks.size()) {
            headerTitle.setText("Все задачи завершены!");
            headerSubtitle.setText("");
            headerSubtitle.setVisible(false);
            headerSubtitle.setManaged(false);
            headerTime.setText("");
        } else if (currentTask != null) {
            headerTitle.setText(currentTask.getTitle());
            if (!currentTask.getSubtitle().isEmpty()) {
                headerSubtitle.setText(currentTask.getSubtitle());
                headerSubtitle.setVisible(true);
                headerSubtitle.setManaged(true);
            } else {
                headerSubtitle.setVisible(false);
                headerSubtitle.setManaged(false);
            }
            headerTime.setText(currentTask.getStartTime() + " - " + currentTask.getEndTime());
        } else {
            ScheduleTask nextTask = getNextTask(now);
            if (nextTask != null) {
                headerTitle.setText("Следующая задача:");
                headerSubtitle.setText(nextTask.getTitle() + " " + nextTask.getSubtitle());
                headerSubtitle.setVisible(true);
                headerSubtitle.setManaged(true);
                headerTime.setText(nextTask.getStartTime() + " - " + nextTask.getEndTime());
            } else {
                headerTitle.setText("Свободное");
                headerSubtitle.setText("время");
                headerSubtitle.setVisible(true);
                headerSubtitle.setManaged(true);
                headerTime.setText("Нет задач");
            }
        }
    }

    private ScheduleTask getCurrentTask(LocalTime now) {
        for (ScheduleTask task : tasks) {
            LocalTime start = LocalTime.parse(task.getStartTime(), DateTimeFormatter.ofPattern("HH:mm"));
            LocalTime end = LocalTime.parse(task.getEndTime(), DateTimeFormatter.ofPattern("HH:mm"));
            if ((now.isAfter(start) || now.equals(start)) && now.isBefore(end)) {
                return task;
            }
        }
        return null;
    }

    private ScheduleTask getNextTask(LocalTime now) {
        for (ScheduleTask task : tasks) {
            LocalTime start = LocalTime.parse(task.getStartTime(), DateTimeFormatter.ofPattern("HH:mm"));
            if (now.isBefore(start)) {
                return task;
            }
        }
        return null;
    }

    private static class ScheduleTask {
        private final String title;
        private final String subtitle;
        private final String startTime;
        private final String endTime;

        @JsonCreator
        public ScheduleTask(
                @JsonProperty("title") String title,
                @JsonProperty("subtitle") String subtitle,
                @JsonProperty("startTime") String startTime,
                @JsonProperty("endTime") String endTime) {
            this.title = title;
            this.subtitle = subtitle;
            this.startTime = startTime;
            this.endTime = endTime;
        }

        public String getTitle() {
            return title;
        }

        public String getSubtitle() {
            return subtitle;
        }

        public String getStartTime() {
            return startTime;
        }

        public String getEndTime() {
            return endTime;
        }
    }
}
