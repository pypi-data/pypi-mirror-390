"""Icon generation for system tray."""

from PIL import Image, ImageDraw


class IconGenerator:
    """Generates tray icons for different application states."""

    COLORS = {
        "idle": "#5E6C84",      # Gray-blue
        "recording": "#E74C3C",  # Red
        "processing": "#F39C12"  # Orange-yellow
    }

    @staticmethod
    def create_icon(state: str, size: tuple[int, int] = (64, 64)) -> Image.Image:
        """
        Create icon for application state.

        Args:
            state: One of "idle", "recording", "processing"
            size: Icon size in pixels (default 64x64)

        Returns:
            PIL Image object

        Raises:
            ValueError: If state is not recognized
        """
        if state not in IconGenerator.COLORS:
            raise ValueError(f"Unknown state: {state}. Must be one of {list(IconGenerator.COLORS.keys())}")

        img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        color = IconGenerator.COLORS[state]
        width, height = size
        padding = int(width * 0.1)

        circle_bbox = [padding, padding, width - padding, height - padding]
        draw.ellipse(circle_bbox, fill=color, outline=color)

        if state == "idle":
            IconGenerator._draw_microphone(draw, width, height, "#FFFFFF")
        elif state == "recording":
            center_x, center_y = width // 2, height // 2
            inner_radius = int(width * 0.15)
            inner_bbox = [
                center_x - inner_radius,
                center_y - inner_radius,
                center_x + inner_radius,
                center_y + inner_radius
            ]
            draw.ellipse(inner_bbox, fill="#FFFFFF")
        elif state == "processing":
            IconGenerator._draw_spinner(draw, width, height, "#FFFFFF")

        return img

    @staticmethod
    def _draw_microphone(draw: ImageDraw.ImageDraw, width: int, height: int, color: str):
        """Draw simple microphone symbol."""
        center_x, center_y = width // 2, height // 2

        mic_width = int(width * 0.15)
        mic_height = int(height * 0.25)
        mic_top = center_y - mic_height // 2

        mic_bbox = [
            center_x - mic_width,
            mic_top,
            center_x + mic_width,
            mic_top + mic_height
        ]
        draw.rounded_rectangle(mic_bbox, radius=mic_width, fill=color)

        stand_width = int(width * 0.05)
        stand_height = int(height * 0.15)
        stand_bbox = [
            center_x - stand_width,
            mic_top + mic_height,
            center_x + stand_width,
            mic_top + mic_height + stand_height
        ]
        draw.rectangle(stand_bbox, fill=color)

        base_width = int(width * 0.2)
        base_height = int(height * 0.04)
        base_bbox = [
            center_x - base_width,
            mic_top + mic_height + stand_height,
            center_x + base_width,
            mic_top + mic_height + stand_height + base_height
        ]
        draw.rectangle(base_bbox, fill=color)

    @staticmethod
    def _draw_spinner(draw: ImageDraw.ImageDraw, width: int, height: int, color: str):
        """Draw simple spinner (three dots)."""
        center_x, center_y = width // 2, height // 2
        dot_radius = int(width * 0.08)
        spacing = int(width * 0.15)

        for i in range(3):
            x = center_x + (i - 1) * spacing
            bbox = [
                x - dot_radius,
                center_y - dot_radius,
                x + dot_radius,
                center_y + dot_radius
            ]
            draw.ellipse(bbox, fill=color)
