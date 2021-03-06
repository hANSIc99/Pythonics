/*
 * This file is part of Pythonic.

 * Pythonic is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * Pythonic is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with Pythonic. If not, see <https://www.gnu.org/licenses/>
 */

#ifndef WORKINGAREA_H
#define WORKINGAREA_H

#include <QFrame>
#include <QGridLayout>
#include <QLoggingCategory>
#include <QJsonObject>
#include <QVector>
#include <QPoint>
#include <QLine>
#include <QPaintEvent>
#include <QPainter>
#include <QPen>
#include <QSize>
#include <QApplication>
#include <QMenu>
#include <QAction>
#include <QList>
#include <QVector>
#include <QStringLiteral>


#include "elementmaster.h"
#include "helper.h"

#define CONNECTION_THICKNESS 5
#define CONNECTION_COLOR QColor(57, 57, 172)
#define CONNECTION_HIGHLIGHT_COLOR QColor(105, 245, 103)
#define MINIMUM_SIZE QSize(1000, 600)
#define SOCKET_OFFSET_POSITION QPoint(45, 61)
#define PLUG_OFFSET_POSITION QPoint(245, 61)

#define BACKGROUND_COLOR_A QColor(54, 106, 151)
#define BACKGROUND_COLOR_B QColor(192, 192, 192)
#define BACKGROUND_COLOR_C QColor(255, 198, 52)

#define SIZE_INCREMENT_X 300
#define SIZE_INCREMENT_Y 150

#define CONN_HIGHLIGHT_TIME 2

struct Connection {
    ElementMaster* parent;
    ElementMaster* child;
    QPen           *pen;
    QLine          connLine;
};

struct ConnectionHighlightInfo {
    Connection  *connection;
    quint32     startTime;
};

/*! @brief Holds the pointer of two connected elements
 *
 *  This class is used to move the connection between elements
 *  in QActions. Used in the context menu for deleting connections.
 *
 *  <a href="https://stackoverflow.com/questions/40764011/how-to-draw-a-smooth-curved-line-that-goes-through-several-points-in-qt">ToDo</a>
 *  @author Stephan Avenwedde
 *  @date October 2020
 *  @copyright [GPLv3](../../../LICENSE)
 */
class ConnectionPair {
    Q_GADGET
public:
    ConnectionPair() : parent(NULL), child(NULL) {};
    ConnectionPair(ElementMaster *parent, ElementMaster *child)
        : parent(parent)
        , child(child){};
    ConnectionPair(const ConnectionPair &other) {
        parent = other.parent;
        child = other.child;
    }

    ~ConnectionPair(){};

    ElementMaster *parent;
    ElementMaster *child;
};
Q_DECLARE_METATYPE(ConnectionPair)



namespace WorkingAreaCmd {

    enum Command {
        HighlightConnection,
        NoCmd
    };
}

/*! @brief WorkingArea holds and manages all programming elements
 *
 *  Detailed description follows here.
 *  <a href="https://stackoverflow.com/questions/40764011/how-to-draw-a-smooth-curved-line-that-goes-through-several-points-in-qt">ToDo</a>
 *  @author Stephan Avenwedde
 *  @date October 2020
 *  @copyright [GPLv3](../../../LICENSE)
 */



class WorkingArea : public QFrame
{
    Q_OBJECT
    const static    QLoggingCategory logC;
    static          WorkingAreaCmd::Command hashCmd(QString const &inString);

public:
    explicit WorkingArea(int areaNo, quint32 *ptrTimer, QWidget *parent = nullptr);

    void registerElement(const ElementMaster *new_element);

    const int                    m_AreaNo;

    /* Connections */
    QVector<Connection>         m_connections;

    void                        updateSize();

    QPen                        m_defaultPen;
    QPen                        m_highlightPen;

    //! Called by the heartbeat (MainWindow)
    void                        m_heartBeat();


signals:

    void stopHighlightAllElements();
    void startExec(quint32 id);
    void stopExec(quint32 id);
    void wsCtrl(const QJsonObject cmd);
    //! Signal is emitted after an element was edited
    void saveConfig();

public slots:

    //! Delete element from WorkingArea
    void deleteElement(ElementMaster *element);
    //! Resize WorkingArea
    void resizeEvent(QResizeEvent *event) override;
    //! Forward to backend and append grid number
    void fwrdWsCtrl(const QJsonObject cmd);
    //! Forward received messages to element
    void fwrdWsRcv(const QJsonObject cmd);
    //! Forward saveConfig signal from ElementMaster to MainWindow
    void saveConfigFwrd();
    //! Slot is called in case of a reconnect
    void clearAllElements();

private slots:

    void disconnectHover(QAction *action);
    void disconnectTrigger(QAction *action);
    void disconnectHide();

protected:

    //! moving elements, drawing connections
    void mousePressEvent(QMouseEvent *event) override;
    //! adding elements,
    void mouseReleaseEvent(QMouseEvent *event) override;
    //! drawing
    void mouseMoveEvent(QMouseEvent *event) override;
    //! draw connection lines
    void paintEvent(QPaintEvent *event) override;

private:

    //! Draw the preview connection during drawing
    void drawPreviewConnection(QPainter *p);
    //! Called from paintEvent
    void drawConnections(QPainter *p);
    void updateConnection();
    //! Called when an element sends an output
    void highlightConnection(quint32 parentId, quint32 childId);

    void createContextMenu(QSet<ElementMaster*> &elementSet,
                           ElementMaster* currentElement,
                           QPoint pos,
                           bool plug);


    const quint32               *m_ptrRefTimer;

    bool                        m_drawing{false};
    bool                        m_startBtnPressed{false};
    bool                        m_openConfig{false};

    /**
     * Pointer to element during drag & drop
     * Pointer to sender element during drawing
     */
    ElementMaster*              m_tmpElement{NULL};


    //!Pointer to receiver element during drawing
    ElementMaster*              m_drawTmpTarget{NULL};

    /* Drag & Drop */

    bool                        m_dragging{false};
    QPoint                      m_dragPosOffset;

    /* Drawing */

    QPoint                      m_drawStartPos;
    QPoint                      m_drawEndPos;
    bool                        m_draw{false};
    bool                        m_mouseOverSocket{false};

    QLine                       m_previewConnection;

    /* Background */

    QLinearGradient             m_backgroundGradient;

    /* Painter */

    QPainter                    m_painter;

    QMenu                       m_contextDisconnect;

    QList<ConnectionPair*>      m_discMenuConnections;

    QVector<ConnectionHighlightInfo> m_highlightedConnections;
};

#endif // WORKINGAREA_H
