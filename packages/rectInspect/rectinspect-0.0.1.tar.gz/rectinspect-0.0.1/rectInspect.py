import cv2
import numpy as np
import skimage.filters as filters
import time

class highlight_defects:
    merged_contours = None

    def __init__(self, threshold_ratio=0.2, min_area=100, width_arr=None, height_arr=None, remove_rec=None):
        self.threshold_ratio = threshold_ratio
        self.min_area = min_area

        # Validate essential parameters
        if (width_arr is None or height_arr is None) and remove_rec is None:
            raise ValueError("You must provide either width_arr/height_arr or remove_rec list")
        if width_arr and height_arr:
            if len(width_arr) != len(height_arr):
                raise ValueError("width_arr and height_arr must have the same length")
            self.ratios = list(zip(width_arr, height_arr))
        else:
            self.ratios = []

        self.remove_rec = remove_rec if remove_rec else []

        # Mouse drawing
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.image = None
        self.clone = None


    '''
    below definition will add different types of filters to inserted img.
    User can insert any img. 
    When add sobel mask,user can define threshold value.According to user input threshold value diffent type of objects will detect.
    '''
    def process_image(self, image_path, threshold_value=None):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        smooth = cv2.GaussianBlur(gray, (33,33), 0)
        division = cv2.divide(gray, smooth, scale=255)
        sharp = filters.unsharp_mask(division, radius=1.5, amount=2.5, preserve_range=False)
        sharp = (255*sharp).clip(0,255).astype(np.uint8)

        gX = cv2.Sobel(sharp, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
        gY = cv2.Sobel(sharp, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=3)
        gradient_magnitude = np.sqrt(gX**2 + gY**2)
        threshold = (threshold_value or self.threshold_ratio) * np.max(gradient_magnitude)
        mgBw = gradient_magnitude > threshold
        mgBw_display = (mgBw * 255).astype(np.uint8)

        kernel = np.ones((5,5), np.uint8)
        morph_img = cv2.morphologyEx(mgBw_display, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mgBw_display, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(morph_img)


        '''
        I remove all detected rectangels which are less than min_area.
        User can define min_area
        '''
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            if area < self.min_area:
                continue
            cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)

        merge_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        merged = cv2.dilate(mask, merge_kernel, iterations=1)
        self.merged_contours, _ = cv2.findContours(merged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        filtered = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return filtered


    '''
    This function will remove unwanted detected objects by filtering using width and height of detected object.
    '''
    def detect_defects(self, filtered, merged_contours):
        detected_items = 0
        detected_top_texts = 0
        updated_flags = [True] * len(self.ratios)

        for cnt in merged_contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Check against remove_rec list (skip boxes near remove_rec pairs)
            skip = False
            for rw, rh in self.remove_rec:
                if abs(w - rw) <= 1 and abs(h - rh) <= 1:
                    skip = True
                    break
            if skip:
                continue

            # If width_arr/height_arr given, check against them
            if self.ratios:
                match_any = False
                for rw, rh in self.ratios:
                    if w <= rw and h <= rh:  # apply detection condition
                        match_any = True
                        break
                if not match_any:
                    continue

            detected_items += 1
            area = w * h
            # print(f"Detected box - w:{w}, h:{h}, area:{area}")

            # Count top texts for first matching ratio
            # for i, (rw, rh) in enumerate(self.ratios):
            #     if updated_flags[i]:
            #         detected_top_texts += 1
            #         updated_flags[i] = False
            #         break

            cv2.rectangle(filtered, (x, y), (x+w, y+h), (0,0,255), 2)

        return detected_items


    '''
    print all defected objects count
    '''
    def print_results(self, detected_items):
        print("Total detected items:", detected_items)


    '''
    save final defect objects in original img.
    '''
    def save_highlited_defect_image(self, filtered, detected_items):
        if detected_items > 4 or (self.ratios != len(self.ratios)):
            print("Defect Detected..............................")
        cv2.imwrite('final.jpg', filtered)
        cv2.destroyAllWindows()


    '''
    draw_rectangle function and draw_rectangle_with_mouse function are related to draw rectangle on img and print 
    that rectangle's width,height and area. 
    '''
    # Mouse callback function
    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
            print(f"Start: ({self.ix}, {self.iy})")

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                img_copy = self.clone.copy()
                cv2.rectangle(img_copy, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
                width = abs(x - self.ix)
                height = abs(y - self.iy)
                area = width * height
                cv2.putText(img_copy, f"W:{width} H:{height} A:{area}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Draw Rectangle', img_copy)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.rectangle(self.image, (self.ix, self.iy), (x, y), (255, 0, 0), 2)
            width = abs(x - self.ix)
            height = abs(y - self.iy)
            area = width * height
            print(f"Final rectangle - width: {width}, height: {height}, area: {area}")
            cv2.imshow('Draw Rectangle', self.image)

    def draw_rectangle_with_mouse(self, image_path):
        # Load image
        self.image = cv2.imread(image_path)
        if self.image is None:
            print("Error: Image not found.")
            return

        # Create a clone for resetting
        self.clone = self.image.copy()

        # Resize window to fit screen but keep full image viewable
        screen_res = 1280, 720
        scale_width = screen_res[0] / self.image.shape[1]
        scale_height = screen_res[1] / self.image.shape[0]
        scale = min(scale_width, scale_height)
        window_width = int(self.image.shape[1] * scale)
        window_height = int(self.image.shape[0] * scale)

        cv2.namedWindow('Draw Rectangle', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Draw Rectangle', window_width, window_height)
        cv2.setMouseCallback('Draw Rectangle', self.draw_rectangle)

        while True:
            cv2.imshow('Draw Rectangle', self.image)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or cv2.getWindowProperty('Draw Rectangle', cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    highlight_defects()
