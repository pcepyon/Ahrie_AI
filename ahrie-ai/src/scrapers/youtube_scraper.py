"""YouTube scraper for fetching K-Beauty medical tourism reviews."""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from datetime import datetime
import re
import asyncio

from src.utils.config import settings

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """
    Scraper for fetching and analyzing YouTube videos about K-Beauty medical tourism.
    """
    
    def __init__(self):
        """Initialize YouTube API client."""
        self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        self.max_results_per_page = 50
        
    async def search_videos(self, 
                          query: str,
                          max_results: int = 50,
                          language: Optional[str] = None,
                          published_after: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos based on query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            language: Language code (e.g., 'ar', 'en', 'ko')
            published_after: Only return videos published after this date
            
        Returns:
            List of video information dictionaries
        """
        try:
            videos = []
            next_page_token = None
            
            # Convert datetime to RFC 3339 format if provided
            published_after_str = None
            if published_after:
                published_after_str = published_after.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            while len(videos) < max_results:
                # Execute search
                request = self.youtube.search().list(
                    q=query,
                    part='snippet',
                    type='video',
                    maxResults=min(self.max_results_per_page, max_results - len(videos)),
                    pageToken=next_page_token,
                    relevanceLanguage=language,
                    publishedAfter=published_after_str,
                    order='relevance'
                )
                
                # Run in executor to make it async
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, request.execute)
                
                # Process results
                for item in response.get('items', []):
                    video_info = self._extract_video_info(item)
                    videos.append(video_info)
                
                # Check for next page
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            # Get additional details for videos
            video_ids = [v['video_id'] for v in videos[:max_results]]
            detailed_info = await self.get_video_details(video_ids)
            
            # Merge detailed info
            for video, details in zip(videos[:max_results], detailed_info):
                video.update(details)
            
            return videos[:max_results]
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {str(e)}")
            return []
    
    def _extract_video_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant information from YouTube search result item.
        
        Args:
            item: YouTube API search result item
            
        Returns:
            Dictionary with extracted video information
        """
        snippet = item['snippet']
        
        return {
            'video_id': item['id']['videoId'],
            'title': snippet['title'],
            'description': snippet['description'],
            'channel_id': snippet['channelId'],
            'channel_title': snippet['channelTitle'],
            'published_at': snippet['publishedAt'],
            'thumbnail_url': snippet['thumbnails']['high']['url'],
            'language': self._detect_language(snippet['title'] + ' ' + snippet['description'])
        }
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character sets.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('ar', 'ko', 'en')
        """
        # Check for Arabic characters
        if re.search(r'[\u0600-\u06FF]', text):
            return 'ar'
        # Check for Korean characters
        elif re.search(r'[\uAC00-\uD7AF]', text):
            return 'ko'
        else:
            return 'en'
    
    async def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for specific videos.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of detailed video information
        """
        try:
            details = []
            
            # Process in batches of 50 (API limit)
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                request = self.youtube.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=','.join(batch_ids)
                )
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, request.execute)
                
                for item in response.get('items', []):
                    details.append(self._extract_detailed_info(item))
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return [{}] * len(video_ids)
    
    def _extract_detailed_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed information from video details response.
        
        Args:
            item: YouTube API video details item
            
        Returns:
            Dictionary with detailed information
        """
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        snippet = item.get('snippet', {})
        
        return {
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'duration': self._parse_duration(content_details.get('duration', '')),
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId', ''),
            'default_language': snippet.get('defaultLanguage', ''),
            'has_captions': content_details.get('caption', 'false') == 'true'
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration to seconds.
        
        Args:
            duration_str: Duration in ISO 8601 format (e.g., 'PT15M30S')
            
        Returns:
            Duration in seconds
        """
        if not duration_str:
            return 0
        
        # Simple parser for PT#H#M#S format
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def get_video_comments(self, 
                               video_id: str,
                               max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get comments for a specific video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to retrieve
            
        Returns:
            List of comment dictionaries
        """
        try:
            comments = []
            next_page_token = None
            
            while len(comments) < max_results:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page_token,
                    order='relevance'
                )
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, request.execute)
                
                for item in response.get('items', []):
                    comment_info = self._extract_comment_info(item)
                    comments.append(comment_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return comments[:max_results]
            
        except HttpError as e:
            # Comments might be disabled
            logger.warning(f"Could not fetch comments for video {video_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting video comments: {str(e)}")
            return []
    
    def _extract_comment_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant information from comment item.
        
        Args:
            item: YouTube API comment thread item
            
        Returns:
            Dictionary with comment information
        """
        snippet = item['snippet']['topLevelComment']['snippet']
        
        return {
            'comment_id': item['id'],
            'text': snippet['textDisplay'],
            'author': snippet['authorDisplayName'],
            'author_channel_id': snippet['authorChannelId']['value'],
            'like_count': snippet['likeCount'],
            'published_at': snippet['publishedAt'],
            'updated_at': snippet['updatedAt'],
            'language': self._detect_language(snippet['textDisplay'])
        }
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get information about a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Dictionary with channel information
        """
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, request.execute)
            
            if response.get('items'):
                item = response['items'][0]
                snippet = item['snippet']
                statistics = item['statistics']
                
                return {
                    'channel_id': channel_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'country': snippet.get('country', ''),
                    'published_at': snippet['publishedAt'],
                    'subscriber_count': int(statistics.get('subscriberCount', 0)),
                    'video_count': int(statistics.get('videoCount', 0)),
                    'view_count': int(statistics.get('viewCount', 0))
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting channel info: {str(e)}")
            return {}
    
    async def search_korean_beauty_reviews(self,
                                         procedure: Optional[str] = None,
                                         clinic: Optional[str] = None,
                                         language: str = 'en') -> List[Dict[str, Any]]:
        """
        Search for Korean beauty medical tourism reviews.
        
        Args:
            procedure: Specific procedure to search for
            clinic: Specific clinic to search for
            language: Target language for results
            
        Returns:
            List of relevant videos
        """
        # Build search query
        query_parts = ['Korea', 'plastic surgery', 'review', 'experience']
        
        if language == 'ar':
            query_parts = ['كوريا', 'تجميل', 'تجربتي', 'عملية']
        elif language == 'ko':
            query_parts = ['성형외과', '후기', '경험']
        
        if procedure:
            query_parts.append(procedure)
        if clinic:
            query_parts.append(clinic)
        
        query = ' '.join(query_parts)
        
        # Search for videos
        videos = await self.search_videos(
            query=query,
            max_results=50,
            language=language
        )
        
        # Filter for relevant videos
        relevant_videos = []
        for video in videos:
            if self._is_relevant_review(video):
                relevant_videos.append(video)
        
        return relevant_videos
    
    def _is_relevant_review(self, video: Dict[str, Any]) -> bool:
        """
        Check if video is a relevant review.
        
        Args:
            video: Video information dictionary
            
        Returns:
            True if video appears to be a relevant review
        """
        # Check title and description for relevant keywords
        text = (video.get('title', '') + ' ' + video.get('description', '')).lower()
        
        relevant_keywords = [
            'review', 'experience', 'journey', 'vlog', 'result',
            'before after', 'تجربتي', 'رحلتي', '후기', '경험'
        ]
        
        exclude_keywords = [
            'trailer', 'news', 'documentary', 'advertisement'
        ]
        
        # Check for relevant keywords
        has_relevant = any(keyword in text for keyword in relevant_keywords)
        has_exclude = any(keyword in text for keyword in exclude_keywords)
        
        # Check video duration (reviews are usually 5+ minutes)
        duration = video.get('duration', 0)
        appropriate_length = 300 <= duration <= 3600  # 5 minutes to 1 hour
        
        return has_relevant and not has_exclude and appropriate_length