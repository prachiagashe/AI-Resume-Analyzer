def generate_recommendations(missing_skills):
    """
    Generate actionable recommendations based on missing skills.
    
    Args:
        missing_skills (list): List of skills present in JD but missing in Resume.
        
    Returns:
        list: Actionable recommendation strings.
    """
    recommendations = []
    
    if not missing_skills:
        recommendations.append("Your resume perfectly matches the required skills for this job!")
        return recommendations
        
    # Generate specific recommendations for missing skills
    for skill in missing_skills:
        # Example mapping for more tailored advice
        if skill.lower() in ["react", "angular", "vue"]:
            recommendations.append(f"Learn {skill} and build frontend projects to showcase it.")
        elif skill.lower() in ["machine learning", "deep learning", "ai"]:
            recommendations.append(f"Build {skill} projects using Scikit-Learn or TensorFlow.")
        elif skill.lower() in ["docker", "kubernetes", "aws", "azure", "gcp"]:
            recommendations.append(f"Gain hands-on experience with {skill} for cloud/deployment roles.")
        elif skill.lower() in ["sql", "mysql", "postgresql"]:
            recommendations.append(f"Practice complex {skill} queries and database design.")
        else:
            recommendations.append(f"Consider learning {skill} or highlighting any related past experience.")
            
    # Add some general best practice recommendations
    recommendations.append("Add measurable achievements (e.g., 'Increased efficiency by 20%').")
    recommendations.append("Ensure your resume uses the exact keywords found in the Job Description.")
    
    # Cap the recommendations so we don't overwhelm the user
    return recommendations[:5]
