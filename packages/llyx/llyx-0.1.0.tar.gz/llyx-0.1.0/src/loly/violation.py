from dataclasses import dataclass


@dataclass
class Violation:
    file: str
    line: int
    code: str
    message: str
    category: str
    severity: str

    @classmethod
    def from_dict(cls, data: dict) -> "Violation":
        return cls(
            file=data["file"],
            line=data["line"],
            code=data.get("code", "LY000"),
            message=data["message"],
            category=data.get("category"),
            severity=data.get("severity"),
        )

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "code": self.code,
            "message": self.message,
            "category": self.category,
            "severity": self.severity,
        }
