"""
ML-Based Recommendation Engine
Uses clustering and collaborative filtering to suggest services and identify premium help needs
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import List, Dict, Tuple
from collections import Counter
import pickle
import os

class RecommendationEngine:
    def __init__(self):
        """Initialize the recommendation engine"""
        self.kmeans_model = None
        self.scaler = StandardScaler()
        self.user_segments = {}
        self.service_similarity = {}
        
        print("🔧 Recommendation Engine initialized")
    
    def analyze_engagement_patterns(self, engagements: List[Dict]) -> Dict:
        """
        Analyze user engagement data to find patterns
        
        Args:
            engagements: List of engagement records from MongoDB
        
        Returns:
            Dict with insights and patterns
        """
        if not engagements:
            return {"message": "No engagement data available"}
        
        df = pd.DataFrame(engagements)
        
        # Basic statistics
        total_engagements = len(df)
        unique_users = df['user_id'].nunique() if 'user_id' in df else 0
        avg_age = df['age'].mean() if 'age' in df else 0
        
        # Service popularity
        service_counts = Counter(df['service'].tolist()) if 'service' in df else {}
        popular_services = dict(service_counts.most_common(10))
        
        # Question frequency
        question_counts = Counter(df['question_clicked'].tolist()) if 'question_clicked' in df else {}
        popular_questions = dict(question_counts.most_common(10))
        
        # Job distribution
        job_counts = Counter(df['job'].dropna().tolist()) if 'job' in df else {}
        
        # Age distribution
        age_distribution = {}
        if 'age' in df:
            df['age_group'] = pd.cut(df['age'].dropna(), 
                                      bins=[0, 18, 25, 40, 60, 100],
                                      labels=['<18', '18-25', '26-40', '41-60', '60+'])
            age_distribution = df['age_group'].value_counts().to_dict()
        
        return {
            "total_engagements": total_engagements,
            "unique_users": unique_users,
            "average_age": round(avg_age, 1),
            "popular_services": popular_services,
            "popular_questions": popular_questions,
            "job_distribution": dict(job_counts),
            "age_distribution": {str(k): v for k, v in age_distribution.items()},
            "timestamp": pd.Timestamp.now().isoformat()
        }
    
    def identify_premium_help_candidates(self, engagements: List[Dict], threshold: int = 3) -> List[Dict]:
        """
        Identify users who need premium help based on repeat engagement patterns
        
        Args:
            engagements: List of engagement records
            threshold: Minimum number of repeat interactions to flag
        
        Returns:
            List of users needing premium help
        """
        df = pd.DataFrame(engagements)
        
        if 'user_id' not in df or 'question_clicked' not in df:
            return []
        
        # Group by user and question
        user_question_counts = df.groupby(['user_id', 'question_clicked']).size().reset_index(name='count')
        
        # Filter users with repeat questions
        premium_candidates = user_question_counts[user_question_counts['count'] >= threshold]
        
        # Enrich with user details
        result = []
        for _, row in premium_candidates.iterrows():
            user_data = df[df['user_id'] == row['user_id']].iloc[0]
            result.append({
                'user_id': row['user_id'],
                'question': row['question_clicked'],
                'repeat_count': int(row['count']),
                'age': user_data.get('age'),
                'job': user_data.get('job'),
                'services_accessed': df[df['user_id'] == row['user_id']]['service'].tolist(),
                'priority': 'high' if row['count'] >= 5 else 'medium',
                'suggested_action': 'Offer live chat support or phone consultation'
            })
        
        return sorted(result, key=lambda x: x['repeat_count'], reverse=True)
    
    def cluster_users(self, engagements: List[Dict], n_clusters: int = 5) -> Tuple[Dict, np.ndarray]:
        """
        Cluster users into segments based on behavior patterns
        
        Args:
            engagements: List of engagement records
            n_clusters: Number of clusters to create
        
        Returns:
            Tuple of (cluster_info, labels)
        """
        df = pd.DataFrame(engagements)
        
        if len(df) < n_clusters:
            return {"message": "Not enough data for clustering"}, np.array([])
        
        # Feature engineering
        features = []
        user_ids = df['user_id'].dropna().unique() if 'user_id' in df else []
        
        for user_id in user_ids:
            user_data = df[df['user_id'] == user_id]
            
            features.append({
                'user_id': user_id,
                'num_engagements': len(user_data),
                'avg_age': user_data['age'].mean() if 'age' in user_data else 0,
                'num_services': user_data['service'].nunique() if 'service' in user_data else 0,
                'num_questions': user_data['question_clicked'].nunique() if 'question_clicked' in user_data else 0,
            })
        
        if not features:
            return {"message": "No user data for clustering"}, np.array([])
        
        feature_df = pd.DataFrame(features)
        X = feature_df[['num_engagements', 'avg_age', 'num_services', 'num_questions']].fillna(0)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply KMeans
        self.kmeans_model = KMeans(n_clusters=min(n_clusters, len(X)), random_state=42)
        labels = self.kmeans_model.fit_predict(X_scaled)
        
        # Analyze clusters
        feature_df['cluster'] = labels
        cluster_info = {}
        
        for cluster_id in range(n_clusters):
            cluster_data = feature_df[feature_df['cluster'] == cluster_id]
            if len(cluster_data) == 0:
                continue
            
            cluster_info[f'segment_{cluster_id}'] = {
                'size': len(cluster_data),
                'avg_engagements': round(cluster_data['num_engagements'].mean(), 1),
                'avg_age': round(cluster_data['avg_age'].mean(), 1),
                'avg_services': round(cluster_data['num_services'].mean(), 1),
                'label': self._label_cluster(cluster_data)
            }
        
        self.user_segments = dict(zip(feature_df['user_id'], labels))
        
        return cluster_info, labels
    
    def _label_cluster(self, cluster_data: pd.DataFrame) -> str:
        """Generate a descriptive label for a cluster"""
        avg_eng = cluster_data['num_engagements'].mean()
        avg_services = cluster_data['num_services'].mean()
        
        if avg_eng > 5 and avg_services > 3:
            return "Power Users"
        elif avg_eng > 3:
            return "Active Users"
        elif avg_services > 2:
            return "Service Explorers"
        else:
            return "Casual Visitors"
    
    def recommend_services(self, user_history: List[str], all_services: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Recommend services based on user history and collaborative filtering
        
        Args:
            user_history: List of services the user has accessed
            all_services: All available services
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended services
        """
        if not user_history:
            # For new users, return most popular services
            return all_services[:top_k]
        
        # Simple collaborative filtering: recommend services accessed by similar users
        recommendations = []
        
        # Find related services (simple approach)
        related_services = self._find_related_services(user_history[0], all_services)
        
        # Filter out services user has already accessed
        for service in related_services:
            if service['name']['en'] not in user_history:
                recommendations.append(service)
            
            if len(recommendations) >= top_k:
                break
        
        return recommendations
    
    def _find_related_services(self, service_name: str, all_services: List[Dict]) -> List[Dict]:
        """Find services related to the given service"""
        # Simple keyword-based similarity (in production, use embeddings)
        keywords = service_name.lower().split()
        
        related = []
        for service in all_services:
            service_text = service['name']['en'].lower()
            score = sum(1 for keyword in keywords if keyword in service_text)
            if score > 0:
                service['similarity_score'] = score
                related.append(service)
        
        return sorted(related, key=lambda x: x.get('similarity_score', 0), reverse=True)
    
    def save_models(self, filepath: str = 'data/ml_models.pkl'):
        """Save trained models to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'kmeans_model': self.kmeans_model,
                'scaler': self.scaler,
                'user_segments': self.user_segments
            }, f)
        
        print(f"✅ Models saved to {filepath}")
    
    def load_models(self, filepath: str = 'data/ml_models.pkl'):
        """Load trained models from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.kmeans_model = data['kmeans_model']
            self.scaler = data['scaler']
            self.user_segments = data['user_segments']
        
        print(f"✅ Models loaded from {filepath}")


# Example usage
if __name__ == "__main__":
    # Initialize recommendation engine
    rec_engine = RecommendationEngine()
    
    # Sample engagement data
    sample_engagements = [
        {'user_id': 'user1', 'age': 25, 'job': 'Student', 'service': 'Ministry of Education', 'question_clicked': 'How to register for exams?'},
        {'user_id': 'user1', 'age': 25, 'job': 'Student', 'service': 'Ministry of Education', 'question_clicked': 'How to register for exams?'},
        {'user_id': 'user1', 'age': 25, 'job': 'Student', 'service': 'Ministry of Education', 'question_clicked': 'How to register for exams?'},
        {'user_id': 'user2', 'age': 45, 'job': 'Teacher', 'service': 'Ministry of Education', 'question_clicked': 'School registration?'},
        {'user_id': 'user3', 'age': 30, 'job': 'Engineer', 'service': 'Ministry of IT', 'question_clicked': 'IT certificate?'},
    ]
    
    # Analyze patterns
    print("📊 Analyzing engagement patterns...")
    patterns = rec_engine.analyze_engagement_patterns(sample_engagements)
    print(f"Total engagements: {patterns['total_engagements']}")
    print(f"Popular services: {patterns['popular_services']}")
    
    # Identify premium help candidates
    print("\n🎯 Identifying premium help candidates...")
    premium_users = rec_engine.identify_premium_help_candidates(sample_engagements, threshold=2)
    for user in premium_users:
        print(f"User {user['user_id']}: {user['question']} ({user['repeat_count']} times) - Priority: {user['priority']}")
    
    # Cluster users
    print("\n👥 Clustering users...")
    clusters, labels = rec_engine.cluster_users(sample_engagements, n_clusters=2)
    print(f"Clusters: {clusters}")
    
    # Save models
    rec_engine.save_models()