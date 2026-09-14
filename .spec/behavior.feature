# Cross-story journeys for cycle EVAL-1.
# 🔴 Only journeys that belong to NO single story. Per-story scenarios live in
#    .spec/aire-docs/implementation/code/behavior/story-<N.M>.feature

Feature: Diagnostics compose without changing gaze behaviour

  @REQ-NF-02 @cross-story
  Scenario: A rejected frame is counted, logged, and still rejected
    Given the unified frame-acceptance envelope from story 1.1
    And the per-reason rejection counters from story 1.2
    And structured logging from story 1.3
    When a feature vector exceeds the live yaw envelope
    Then the frame is rejected exactly as it was before this cycle
    And the "yaw" rejection counter increments by exactly one
    And no log record contains frame or landmark data

  @REQ-F-01 @REQ-F-02 @cross-story
  Scenario: Calibration and live gates disagree only by their documented deviation
    Given a feature vector inside the live envelope but outside the calibration envelope
    When the vector is evaluated at both call sites
    Then the live site accepts it
    And the calibration site rejects it
    And the difference is attributable to a named deviation, not an independent literal
