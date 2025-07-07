import os
import cv2
import numpy as np
import random
import glob

class DatasetAugmentor:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.class_counts = {}
        
    def count_images_per_class(self):
        """Count images in each class folder"""
        for class_name in os.listdir(self.dataset_path):
            class_path = os.path.join(self.dataset_path, class_name)
            if os.path.isdir(class_path):
                image_files = [f for f in os.listdir(class_path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                self.class_counts[class_name] = len(image_files)
        
        print("Current class distribution:")
        for class_name, count in self.class_counts.items():
            print(f"{class_name}: {count} images")
        return self.class_counts
    
    def rotate_image_white_padding(self, image, angle_range=(-10, 10)):
        """Rotate image by random angle with white padding"""
        angle = random.uniform(angle_range[0], angle_range[1])
        rows, cols = image.shape[:2]
        
        # Calculate rotation matrix
        M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
        
        # Apply rotation with white background
        rotated = cv2.warpAffine(image, M, (cols, rows), borderValue=(255, 255, 255))
        
        return rotated
    
    def augment_class(self, class_name, class_path, current_count):
        """Augment images for a specific class based on count"""
        print(f"\nProcessing class '{class_name}' with {current_count} images...")
        
        # Get all image files
        image_files = glob.glob(os.path.join(class_path, "*.png")) + \
                     glob.glob(os.path.join(class_path, "*.jpg")) + \
                     glob.glob(os.path.join(class_path, "*.jpeg"))
        
        if current_count >= 600:
            # Take 30 random images and augment them
            selected_files = random.sample(image_files, min(200, len(image_files)))
            target_augs = 200
            print(f"  Strategy: Augmenting 30 random images from {current_count}")
            
        elif current_count >= 320:
            # Create 1x copy (same number of augmented images as original)
            target_augs = current_count
            selected_files = image_files.copy()
            print(f"  Strategy: Creating {target_augs} augmented images (1x copy)")
            
        elif current_count >= 150:
            # Create 3x copy
            target_augs = current_count * 3
            selected_files = image_files * 3
            print(f"  Strategy: Creating {target_augs} augmented images (3x)")
            
        else:
            # Create 5x copy, targeting ~400 images
            target_augs = max(400, current_count * 5)
            multiplier = target_augs // current_count + 1
            selected_files = image_files * multiplier
            selected_files = selected_files[:target_augs]
            print(f"  Strategy: Creating {target_augs} augmented images (targeting 400+)")
        
        # Apply rotation augmentation
        aug_count = 0
        for i, img_path in enumerate(selected_files):
            try:
                # Read image
                if img_path.lower().endswith('.png'):
                    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                else:
                    image = cv2.imread(img_path)
                
                if image is None:
                    continue
                
                # Apply rotation with white padding
                rotated = self.rotate_image_white_padding(image)
                
                # Save augmented image
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                ext = os.path.splitext(img_path)[1]
                aug_filename = f"{base_name}_rot_{i}{ext}"
                aug_path = os.path.join(class_path, aug_filename)
                
                cv2.imwrite(aug_path, rotated)
                aug_count += 1
                
                if aug_count % 50 == 0:
                    print(f"  Processed {aug_count}/{len(selected_files)} images")
                    
            except Exception as e:
                print(f"  Error processing {img_path}: {e}")
                continue
        
        print(f"  Completed: Added {aug_count} augmented images")
        return aug_count
    
    def augment_dataset(self):
        """Augment the entire dataset"""
        print("Starting dataset augmentation with rotation only...")
        
        # Count current images
        self.count_images_per_class()
        
        total_added = 0
        
        for class_name, count in self.class_counts.items():
            class_path = os.path.join(self.dataset_path, class_name)
            
            if not os.path.isdir(class_path):
                continue
            
            added = self.augment_class(class_name, class_path, count)
            total_added += added
        
        print(f"\n=== Augmentation Complete ===")
        print(f"Total images added: {total_added}")
        
        # Show final distribution
        print("\nFinal class distribution:")
        self.count_images_per_class()

# Usage
if __name__ == "__main__":
    # Set your dataset path here
    dataset_path = "/content/drive/MyDrive/datasets/test-yolo-2-4-annotations/char_dataset-english-labels-before-aug"  # Change this to your dataset path
    
    # Create augmentor instance
    augmentor = DatasetAugmentor(dataset_path)
    
    # Run augmentation
    augmentor.augment_dataset()
