function setSkillLevel(level) {
    fetch('/set_skill_level', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({level: level})
    }).then(() => location.reload());
}