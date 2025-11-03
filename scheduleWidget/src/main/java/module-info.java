module com.widget.schedule {
    requires javafx.controls;
    requires javafx.fxml;

    opens com.widget.schedule to javafx.fxml;
    exports com.widget.schedule;
}