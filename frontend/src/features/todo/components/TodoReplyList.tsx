import { TodoComment } from "@/shared/types";

type Props = {
  comments: TodoComment[];
};


export default function TodoReplyList({comments} : Props) {
    return(
        
        <div className="comment-list" id="commentList">
            {
                comments.length === 0 ? (
                    <div className="comment-item text-center">
                        등록된 댓글이 없습니다.
                    </div>
                ) : (
                    comments.map((comment, _) => (
                        <div key={`${comment.commentId}`} className="comment-item">
                            <div className="avatar av1">{comment.author.charAt(0)}</div>
                            <div className="comment-body-wrap">
                                <div className="comment-meta-line">
                                    <span className="comment-author">{comment.author}</span>
                                    <span className="comment-date">{comment.lastModified}</span>
                                </div>
                                <div className="comment-text">{comment.commentText}</div>
                            </div>
                            {/* 
                            <button className="x-btn" title="댓글 삭제">✕</button>
                            */}
                        </div>
                    ))
                )
            }
        </div>
        
       
    );
}